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