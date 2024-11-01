TODO:


find more neurodegenerative data, also label the algorithms. and think of a strategy


**Meeting 01.11.24**

Where have you made progress?

- excel sheet for overview
- use MetaPhlAn3 to generate taxonomic profiles
- trained first model on some taxonomic profiles we already have
    -> random forest regression, acc=0.69
- started working on feature extraction (pca, ...)
- trying this out: http://epistasislab.github.io/tpot/

Where did you struggle?

- didn't really find more data
- unsure if enough data
- unsure how to use taxonomic profiles as dataset, we don't understand the data
    -> do you know what part of microbiome is specifically important? maybe talk to biology expert?

What are your key ideas on how to overcome your struggles?

- look into methods for unbalanced datasets
examples:
- oversampling, undersampling
- data augmentation 

possible plans for next week:

- work more on models, feature extraction
- look at what models other people used for classification of taxonomic profiles
- use MetaPhIAn3 to generate more taxonomic profiles
- We don't know if it makes sense invest more time into finding more data
- access to cluster would be nice