TODO:


find more neurodegenerative data, also label the algorithms. and think of a strategy


**Meeting 01.11.24**

Where have you made progress?

- csv sheet for overview
- use MetaPhlAn3 to generate taxonomic profiles
- trained first model on some taxonomic profiles we already have
    -> random forest regression, acc=0.69
- started working on feature extraction (pca, ...)
- trying out different pipelines using [tpot](http://epistasislab.github.io/tpot/)


Where did we struggle?
- didn't really find more data
- unsure if enough data
- unsure how to use taxonomic profiles as dataset, we currently have trouble understanding the data
    -> what part of microbiome is specifically important? maybe talk to biology expert?

Key ideas on how to overcome our struggles?

- look into methods for unbalanced datasets
examples:
- oversampling, undersampling
- data augmentation

possible plans for next week:
- maybe look for more diseases for example: Huntington's disease (HD)
- work more on models, feature extraction
- look at what models other people used for classification of taxonomic profiles
- use MetaPhIAn3 to generate more taxonomic profiles
- We don't know if it makes sense invest more time into finding more data
- access to cluster would be nice


results of running tpot on the taxanomic profiles with:
    - 490 patients with Parkinson's (PD) | 234 healthy control patients.
    - Best pipeline: ExtraTreesClassifier(input_matrix, bootstrap=False, criterion=entropy, max_features=0.45, min_samples_leaf=6, min_samples_split=14, n_estimators=100)
    - TPOT Test Accuracy: 0.8278145695364238

Next step:
shuffeling this data, with the '8000 healty/control patients' taxanomic profiles and running tpot again





## Importan cluster links:
    - usage tutorial: ./SAFARI_Cluster_Tutorial.pdf
    - login tutorial: ./SAFARI Cluster Guide.pdf


    using a docker container:

    docker pull globusgenomics/metaphlan3
    https://hub.docker.com/r/globusgenomics/metaphlan3


    cookbook for athome:
    docker pull globusgenomics/metaphlan3:latest
    docker save globusgenomics/metaphlan3:latest -o docker_metaphlan3.tar
    ./upload_to_cluster.sh
    docker load -i /home/ehanelt/metaGclub/docker_metaphlan3.tar
    USE SRUN TO RUN:
    tar -xf filename.tar -C /metaphlan3-container
    docker run -d --name metaphlan3-container -p 8080:80 globusgenomics/metaphlan3:latest
    srun "docker build metaphlan3 . 8080:80"



how to use conda to run metaphlan3:
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda create -n <env-name> -c bioconda -c conda-forge python=3.7 metaphlan=3.0


https://training.galaxyproject.org/training-material/topics/microbiome/tutorials/taxonomic-profiling/tutorial.html


we want the genome based approach

SRA TOOLS IS A REQUIREMENT AND BIOPYTHON