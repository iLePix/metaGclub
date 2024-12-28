import os
import csv
import time
import subprocess
from Bio import Entrez
import xml.etree.ElementTree as ET
from tqdm import tqdm

# ----------------------------
# User variables
# ----------------------------
Entrez.email = "ilepixmc@gmail.com"  # Your email for NCBI queries
bioproject_id = "601994"

# Output filenames and directories
biosample_ids_file = "all_biosample_ids.txt"
xml_cache_dir = "biosample_xml_cache"
biosample_metadata_file = "biosample_metadata.csv"
sra_download_dir = "./fastq_files"

# Number of retries for failed requests
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5  # Delay between retries (in seconds)

# ----------------------------
# Helper function: fetch with retry
# ----------------------------
def fetch_xml_with_retry(db, record_id, rettype="xml", retmode="text"):
    """
    Attempt to fetch XML data from NCBI Entrez, retrying on failure up to MAX_RETRIES times.
    Returns the text/XML on success, or None if all retries fail.
    """
    attempt = 1
    while attempt <= MAX_RETRIES:
        try:
            handle = Entrez.efetch(db=db, id=record_id, rettype=rettype, retmode=retmode)
            data = handle.read()
            handle.close()
            # If data is bytes, decode
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return data
        except Exception as e:
            print(f"[Attempt {attempt}/{MAX_RETRIES}] Error fetching {record_id} from {db}: {e}")
            if attempt == MAX_RETRIES:
                print(f"  Giving up on {record_id} after {MAX_RETRIES} attempts.\n")
                return None
            else:
                attempt += 1
                time.sleep(RETRY_DELAY_SECONDS)

# ----------------------------
# 1. Fetch BioSample IDs linked to the BioProject
# ----------------------------
print("Fetching BioSample IDs...")
handle = Entrez.elink(dbfrom="bioproject", db="biosample", id=bioproject_id)
record = Entrez.read(handle)
handle.close()

biosample_ids = []
for linkset in record:
    if "LinkSetDb" in linkset:
        for link_db in linkset["LinkSetDb"]:
            for link in link_db["Link"]:
                biosample_ids.append(link["Id"])

biosample_ids = list(set(biosample_ids))  # Deduplicate if needed
print(f"Collected {len(biosample_ids)} BioSample IDs.")

# Save BioSample IDs to a file
with open(biosample_ids_file, "w") as id_file:
    for biosample_id in biosample_ids:
        id_file.write(biosample_id + "\n")

print(f"BioSample IDs saved to {biosample_ids_file}.")

# ----------------------------
# 2. Fetch and cache BioSample XML
# ----------------------------
print("Fetching and caching BioSample metadata...")
os.makedirs(xml_cache_dir, exist_ok=True)

for biosample_id in tqdm(biosample_ids, desc="Caching Metadata", unit="BioSample"):
    xml_file = os.path.join(xml_cache_dir, f"{biosample_id}.xml")
    if not os.path.exists(xml_file):
        metadata = fetch_xml_with_retry(db="biosample", record_id=biosample_id)
        if metadata is not None:
            with open(xml_file, "w") as file:
                file.write(metadata)

print(f"Metadata cached in {xml_cache_dir}.")

# ----------------------------
# 3. Collect unique BioSample attribute fields
# ----------------------------
print("Discovering all unique fields from cached XML...")

# We'll store standard fields:
#   - BioSample ID
#   - SRS ID (if found in <Ids> block)
#   - SRR IDs (found by fetching the SRA record for the SRS)
all_fields = set(["BioSample ID", "SRS ID"])
attribute_names = set()

for biosample_id in tqdm(biosample_ids, desc="Inspecting Cached Metadata", unit="BioSample"):
    xml_file = os.path.join(xml_cache_dir, f"{biosample_id}.xml")
    if not os.path.exists(xml_file):
        continue

    with open(xml_file, "r") as file:
        metadata = file.read()
    if not metadata.strip():
        continue

    try:
        root = ET.fromstring(metadata)
        # Grab attribute names
        attributes = root.find(".//Attributes")
        if attributes is not None:
            for attribute in attributes:
                attribute_names.add(attribute.attrib["attribute_name"])
    except ET.ParseError:
        pass

all_fields.update(attribute_names)
all_fields = list(all_fields)  # stable ordering
print(f"Discovered {len(all_fields)} total fields:\n{all_fields}")

# ----------------------------
# 4. Build CSV: parse BioSample for SRS, then fetch SRA XML for runs
# ----------------------------
print("Building CSV...")

with open(biosample_metadata_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(all_fields)  # header

    for biosample_id in tqdm(biosample_ids, desc="Writing Metadata", unit="BioSample"):
        # Prepare a row dictionary
        row_data = {field: "N/A" for field in all_fields}
        row_data["BioSample ID"] = biosample_id

        xml_file = os.path.join(xml_cache_dir, f"{biosample_id}.xml")
        if not os.path.exists(xml_file):
            writer.writerow([row_data[f] for f in all_fields])
            continue

        with open(xml_file, "r") as file:
            metadata = file.read()
        if not metadata.strip():
            writer.writerow([row_data[f] for f in all_fields])
            continue

        # Parse the BioSample XML
        try:
            root = ET.fromstring(metadata)
            # (a) Extract SRS from <Ids><Id db="SRA">SRSxxxxx</Id>
            srs_id = None
            ids_block = root.find(".//Ids")
            if ids_block is not None:
                for id_el in ids_block.findall("Id"):
                    db_attr = id_el.attrib.get("db")
                    if db_attr and db_attr.lower() == "sra":
                        val = id_el.text.strip()
                        # If it starts with SRS (or ERS/DRS), treat it as SRA Sample
                        if val.upper().startswith(("SRS", "ERS", "DRS")):
                            srs_id = val
                            row_data["SRS ID"] = srs_id
                            break

            # (b) Extract BioSample attributes
            attributes = root.find(".//Attributes")
            if attributes is not None:
                for attribute in attributes:
                    field_name = attribute.attrib["attribute_name"]
                    field_value = attribute.text or "N/A"
                    if field_name in row_data:
                        row_data[field_name] = field_value

        except Exception as e:
            print(f"Error parsing BioSample {biosample_id}: {e}")

        # Write the row
        writer.writerow([row_data[f] for f in all_fields])

print(f"CSV built: {biosample_metadata_file}")

# ----------------------------
# 5. Download FASTQ files WITHOUT splitting
# ----------------------------
print("Downloading FASTQ files...")
os.makedirs(sra_download_dir, exist_ok=True)

# Read the CSV to find all SRR IDs
fastqs_to_download = []

with open(biosample_metadata_file, "r", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        biosample_id = row.get("BioSample ID", "N/A")
        if biosample_id != "N/A":
            biosample_id = f"SAMN{biosample_id}"  # Append SAMN to BioSample ID
            fastqs_to_download.append(biosample_id)


# Use fastq-dump for each SRR, no '--split-files'
for biosample_id in tqdm(sorted(fastqs_to_download), desc="Downloading FASTQs", unit="Run"):

    cmd = [
        "fastq-dump",
        biosample_id,
        "-O", sra_download_dir,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"\nAll FASTQ files downloaded into '{sra_download_dir}'. One file per run with SAMN prepended to BioSample ID.")

