##

# CSC413 Final Project Report:

# Zeroshot Unsupervised Machine Translation Model

Francis Dinh

Nicholas Tubielewicz

Nicholas Wong

Yash Agarwal

**Introduction:**

Our goal was to create a zeroshot-capable machine translation model through fully unsupervised learning. For low resource languages or pairs of languages that do not have many translation examples, traditional supervised models cannot be used, so we attempt to create a model given the course's material that would potentially be capable of translating between languages with few true examples. The goal of our project will be mostly a proof of concept to see if this method is viable across a set of languages: French, Arabic, Luxembourgish, and Japanese, each given their own model. Our input will be a sentence from one of these languages and we expect that the model will output the sentence translated into English. We employ a sequence-to-sequence model to learn these other languages and apply the ideas presented in the GAN lectures to attempt to "translate" sentence embeddings from one language to our target language English.

**Model Figure:**

![](assets/image13.png)

The first model is a monolingual generator that uses transformer encoders and decoders in order to generate language embeddings in a singular language. It is designed so that a sequence of text is passed through the transformer encoder model to generate a sequence of embeddings, then the decoder takes the language specific embeddings and returns the same text sequence. The transformer model becomes our expert in some source language during its learning process to optimize the speed and quality of the embeddings of the chosen language. These embeddings will then be transformed into our target language's (English) embeddings.

The second model utilizes Contrastive Language Image Pre-training (CLIP) generated embeddings during training. CLIP was designed to combine the embedding space of images and text which we hypothesized would help our model produce more "abstract" embeddings of sentences. We used a pre-trained model since obtaining zero-shot translations is an integral part of this research project. In order to make sense of CLIP's embeddings, we built a decoder network from only transformer decoders that would take the CLIP embeddings for a sentence and reproduce that same English sentence. The goal of this model was to be able to receive an embedding, then produce the sentence represented by said embedding.

The final two models are a discriminator and a translator (acting as a sort of "generator") that is utilized to map embeddings from one language to another. The discriminator helps our model to be able to distinguish real English embeddings from translated ones, effectively an adversary to our translator model, pushing it to generate better looking English embeddings. The generator portion of the model uses our source language's sentence embeddings and acts as a domain-transfer model mapping embeddings in a host language to a target language. The translation generator model learns to generate better embeddings to eventually "trick" the discriminator with good enough faux English embeddings. The second part of training this model is similar to cycle GAN where we train another part of the translator to reproduce the same embeddings it was given as source from English back into its source language, this was hypothesized to ensure our model was learning to extract proper features that it would be able to reconstruct in the embedding space.

For the true forward pass that is the goal of our model, our goal would be taking a sentence in one language (i.e. Japanese) and producing its translation in our target language (i.e. English). Firstly, the Japanese sentence would be tokenized (we used a multilingual byte-pair encoding) and then fed into our transformer encoder-decoder network, where we will extract only the embeddings from the encoder part. The embeddings would then be fed into the "translator" model which we hope would take the Japanese embeddings and translate/transfer them to the domain of English embeddings. From there, we pass these generated English embeddings to our CLIP-trained decoder to generate our final English sentence such that if the embeddings were transferred perfectly, we would get a perfect translation from Japanese to English (or any other language pair we would have trained).

**Model Parameters:**

The total number of trainable parameters is 273522367 across all four models. The per-model breakdown is as follows:

The sequence-to-sequence transformer model contains 139366139 trainable parameters. This includes 61208064 in the embedding layer, 6311936 in the encoder, 10518528 in the decoder, and 61327611 in the final fully-connected layer.

The second CLIP transformer model contains a total of 133054203 trainable parameters, with 61208064 in the embedding layer, 10518528 in the decoder, and 61327611 in the final layer.

The discriminator contains 51401 parameters.

The translator contains 1050624 parameters, split equally between the two transfer learning function layers.

**Model Examples:**

![](assets/image3.png)

The image above consists of a model that is working on an overfit model and is able to successfully run a translation

![](assets/image5.png)

Unsuccessful Model on French testset, decoder trained improperly leading to poor translations

**Data Source:**

The datasets used are from Huggingface. They are the [wikipedia](https://huggingface.co/datasets/wikipedia), [aiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101](https://huggingface.co/datasets/SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101), and [AhmedSSabir/Japanese-wiki-dump-sentence-dataset datasets](https://huggingface.co/datasets/AhmedSSabir/Japanese-wiki-dump-sentence-dataset).

Tatoeba: [https://huggingface.co/datasets/tatoeba](https://huggingface.co/datasets/tatoeba)

A dataset of human-translated sentences across many pairs of languages. This set was not used once in training, only during evaluation of its performance since our goal was zeroshot translations.

**Data Summary:**

There are a number of datasets being used in the model, they consist of English, French, Arabic, Luxembourgish and Japanese.

The English, French, and Luxembourgish data are from the Wikipedia dataset on Huggingface. The link to the dataset is [https://huggingface.co/datasets/wikipedia](https://huggingface.co/datasets/wikipedia). It contains a dump of cleaned Wikipedia articles, used in training well-known models such as BERT, with 6,458,670 from the 20220301.en subset alone. The English dataset contains a vocabulary size of 40,000, 5 million tokens and an average length of each document is about 800 tokens. The most common word is "the" with frequency is 405,222, average frequency of a word is 89 words, average sentence length is about 19 words.

The French dataset contains a vocabulary size of 50,000, 10 million tokens and an average length of each document is about 1000 tokens. The most common word is "de" with frequency is 312,247, average frequency of a word is 89 words, average sentence length is about 19 words.

The Luxembourgish dataset contains a vocabulary size of 30,000, 2 million tokens and an average length of each document is about 600 tokens. The most common word is "an" with frequency is 14,027, average frequency of a word is 20 words, average sentence length is about 12 words. An actually means "in the" if translated into English.

The licensing for most of Wikipedia's text and many of its images are co-licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License (CC BY-SA) and the GNU Free Documentation License (GFDL) (unversioned, with no invariant sections, front-cover texts, or back-cover texts).

Arabic dataset is from the SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101 dataset on Huggingface, link to the dataset is [https://huggingface.co/datasets/SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101](https://huggingface.co/datasets/SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101). It also contains a dump of cleaned Wikipedia articles, used in training well-known models such as BERT, it contains about 5,000 sentences. The Arabic dataset contains a vocabulary size of 60,000, 7 million tokens and an average length of each document is about 1200 tokens. The most common word is "في" with frequency is 201,321, average frequency of a word is 42 words, average sentence length is about 25 words. في is the word for "in" in Arabic. Most of Wikipedia's text and many of its images are co-licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License (CC BY-SA) and the GNU Free Documentation License (GFDL) (unversioned, with no invariant sections, front-cover texts, or back-cover texts) and this is no different.

Japanese dataset is from AhmedSSabir/Japanese-wiki-dump-sentence-dataset on Huggingface which you can accessing the following link:

[https://huggingface.co/datasets/AhmedSSabir/Japanese-wiki-dump-sentence-dataset](https://huggingface.co/datasets/AhmedSSabir/Japanese-wiki-dump-sentence-dataset).

The japanese dataset contains a dump of cleaned Wikipedia articles, used in training well-known models such as BERT, it contains about 55,000 sentences. The Japanese dataset contains a vocabulary size of 70,000, 8 million tokens and an average length of each document is about 900 tokens. The most common word is "の" with frequency is 440,282, average frequency of a word is 194 words, average sentence length is about 20 words. の is the Japanese word for "on". Most of Wikipedia's text and many of its images are co-licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License (CC BY-SA) and the GNU Free Documentation License (GFDL) (unversioned, with no invariant sections, front-cover texts, or back-cover texts).

**Data Transformation:**

The first step in data transformation was to download the data in its original format which is a collection of text files in various languages such as English, French, Arabic, Luxembourgish and Japanese.

The data transformation is a lengthy process with many steps, the first of which is tokenizing the loaded dataset(s). This is done using the BERT multilingual pretrained model, it breaks up the data into usable tokens. After this process is complete, the loaded dataset is split into 3 subsets consisting of train, validation and test datasets. This is in order to allow our model to be able to use a variety of dedicated datasets in order to compute various results. After the data is split, we use a clip encoder and the tokens we generated to create a dictionary for each sub-dataset. Additionally, we take our wikipedia dumps and separate all the text into sentences. Data is cleaned up by removing any extremities (such as '/n') and reformatting sentences so it is readable by our models. For the English dataset we create clip embeddings for each sentence using OpenAI clip. We have 3 dictionaries for each subset containing the keys; sentences, clip embeddings and tokens. We only fill in clip embeddings if we need to access english data or else it is left blank. This process of creating our dictionary sets is done after the processing of all other information, so that data transformation is complete.

It is important to note that we have set a limit for how many sentences we process via a parameter in our data loader to accommodate for computation time and restrictions based on OpenAI clip. The sentences that are in our dataset are also also parsed by our model so that sentences that are too long or repetitive in nature are omitted in order to produce the best possible results.

**Data Split:**

We have chosen to split our data by index due to wikipedia being our primary source for our datasets. The data consists of a 80-10-10 split, to prioritize the data being used for training, the remaining 20% can be divided into tuning our hyperparameters via the validation set and the accuracy of our translations using the test set.

**Training Curve:**

The decoder was trained separately from the rest of the models for 200 epochs as it only depends on English language data. This allows the other models for the different languages to be trained much quicker as they can all share the same decoder model without affecting accuracy.

![](assets/image6.png) ![](assets/image12.png)
![](assets/image7.png) ![](assets/image4.png)

Due to our goal being translations from unsupervised data, we used the probability of the discriminator correctly judging the English Embeddings vs the other Language Embeddings as a measure of accuracy in our model.

**Hyperparameter Tuning:**

We have tuned our hyperparameters through our function parameters being defaulted to the best parameters that we have found by checkpointing epochs. Some hyperparameters such as the batch size and number of sentences per dataset had to be cut down due to gpu limits. Otherwise we extensively trained our models and studied the impact of tuning hyperparameters via our train function that utilizes all of them in a single function. Additionally, the training can be broken down into separate training functions that operate just one of our models at a time to combat gpu limits and overall training time. As mentioned, we trained the decoder separately, cutting the total train time of the entire model by half per epoch (300 second to 150 seconds).

Our multiple models have different levels of hyperparameter tuning that can be done, the key parameters are explained below:

Transformer, Decoder:

- Ntoken: this parameter affects the vocabulary size of our input language, adjusting this results in greater generalizability
- d_model: The number of hidden representations in the model, adjusting this results in a higher quality of sentence generating but increases training time
- d_hid: the size of hidden layers in the model, adjusting this results in a higher quality of sentence generating but increases training time
- nlayers: the size of hidden layers in the model, adjusting this results in a higher quality of sentence generating but increases training time
- dropout: this represents the dropout rate at which information is dropped out of the network, increasing this parameter helps prevent overfitting.

Translator:

- i_embed_size, o_embed_size: the input and output size of the translator model, adjusting this parameter led to minor changes in the quality of data representation but was not worth it due to time increasing substantially
- nlayers: the size of hidden layers in the model, adjusting this results in a higher quality of sentence generating but increases training time
- hidden: the number of hidden units in the translator layer, this was the most substantial parameter as it helped in generate sentences that were more structurally sound

Discriminator:

- number of layers: we selected to stay in one layer as increasing made it too complex, during training the loss would rapidly decrease which increased the loss of the translator

**Quantitative Measures:**

The measures that we will be using to evaluate our results is our translation quality after going through the model, the objective is to have the model be translated into one of our supported languages (french, arabic, luxembourgish and japanese) and undergo changes consisting of encoding, tokenizing, translating and decoding to obtain a sentence similar to the original english language without any supervision. This unsupervised nature means that most of the work will be done by the model without any targets, so the output will not be influenced by any factors other than the model itself.

**Quantitative and Qualitative Results:**

Our results showcase the models' translations and the probabilistic measure we used for tracking the discriminator so that the translation model is generating other language embeddings similar to an english embedding. The results are shown for each language we chose, however, noticeably the translations are not what we expected.

_Quantitative Results:_

_French Quantitative Results:_

![](assets/image15.png)

![](assets/image14.png)

_Arabic Quantitative Results:_

![](assets/image16.png)

![](assets/image2.png)

_Luxembourgish Quantitative Results:_

![](assets/image10.png)

![](assets/image1.png)

_Japanese Quantitative Results:_

![](assets/image11.png)

Surprisingly "This will cost 30 euros" did pick up on the word sell, also the ability to predict some number. Some knowledge of Japanese however reveals the source sentence translates more literally to "30 euros this will become" so it is difficult to know if our model really learned the context of selling/cost through the currency name alone.

![](assets/image9.png)

_Qualitative Results:_

In our model, we found that the training losses showed that the models were training properly and the discriminator was able to successfully identify the real from fake embeddings but upon running the full model rather than the training function, it was apparent that the discriminator was only able to reach a maximum probability classification of about 50% at best and often lower than that at around 55-60%. The consequence of this was evident in our quantitative results when looking at the translations.

**Justification of Results:**

_Design Choice Justification:_

We hypothesized that a multilingual embedding space would compromise on the quality of reconstructing sentences. The idea for having each language with its own embedding space was the potential for low resource languages that did not have many cross-language translations available. Monolingual embedding spaces are tangible to generate, and if we can show our design of translating between embedding spaces works, then we would have shown that deep learning can be translators between languages with few to no actual translational data available.

_Language Selection Justification:_

In order to evaluate how well our model would work with different languages, we chose four different languages based on how difficult they were to translate to English and the availability of textual data available.

The four languages chosen were:

- Japanese
  - High difficulty/high availability
- Arabic
  - High difficulty/low availability
- Luxembourgish
  - Low difficulty/low availability
- French
  - Low difficulty/high availability

For low resource languages, we were able to create an embedding space for itself for the tokens generated for these sentences in the hopes of generating a multilingual space. We envisioned this assisting the translator being able to better understand context and be able to better translate the language itself. After experimenting, we decided to create one hot vector tokens for not only low resource languages but all languages alongside the sentences for languages including English.

_Hypothesis for why the implemented method does not perform reasonably:_

The primary objective of the model was to build a good translator by utilizing a multilingual CLIP as the model is pre-trained on many languages including all of the languages that we use in English, French, Arabic, Luxembourgish and Japanese. An important issue in our model was that a powerful encoder and decoder was needed in order to correlate English to a language and be able to complete the translation without any supervision. However we had not stress tested our discriminator which resulted in improper translations when running the model. As a result, the decoder was unable to generate proper sentences with appropriate context and sentence structure. We wished our zero-shot machine translation model to be unsupervised and be able to complete the task without any data augmentation as it was the main crux of our research project. Due to this unsupervised nature, hints or synthetic data could not be provided in order to assist the machine translation model.

_What we could have changed to improve our project:_

In terms of code, we only used the most elementary of transformer architectures for our models, not using current developments in the fields or even technologies such as BERT for our encoder to produce better embeddings or reformers for memory efficiency. We could also have used more pretrained language models instead of wasting our time training models that are already trained with very similar architecture, for example GPT (even version 1) to use for our decoder. Our goal for the project was overly ambitious and out of scope for the time and resources we had available. Considering the boom of large language models in today's space and the many parameters + training time required for them to perform well generally. We were not capable of training models with good language understanding capabilities whether by lack of physical resources (disk space, GPU memory, RAM) or shortness of time.

**Ethical Considerations:**

Some of the ethical considerations in this model include biases, fairness, privacy, accuracy and transparency. One of the largest ethical considerations to take note of is the bias present in the source datasets that is used in our model. Bias can be inflicted onto the model in many ways such as toxicity, discriminatory behaviour, ignorance or hyperfixation on some unnecessary features. It is crucial that the data set is carefully adjusted to remove as much bias as possible not only in the resulting output but also in the model itself so that the results are not skewed.

Fairness is also an ethical consideration as the training data may not be expansive enough which might lead to inaccuracies or misutilization of all groups who might need to use the language model. Additionally, some dialects and languages are more vulnerable to mistranslations where they may be underfitted or overfitted. Additionally, many languages include the use of gendered words which is another factor that the model would need to accurately compute and work around to ensure output diversity is high and no culture is left out. Due to the high standard of fairness present in the model, it is imperative that the model created also follows these by producing accurate, inclusive and culturally appropriate results.

Privacy is a massive contributor to being ethical considerate as the project may be used for sensitive documents or for personal information which should be secure and that the user data should not be used for anything other than the model as privacy regulations must be followed.

Accuracy is another important ethical consideration and a limitation of our model as machine translations are prone to producing inaccurate translations which can result in poor user experiences. An important factor to consider is the training accuracy vs precision where accuracy is how close the results are to what it is supposed to be and precision is how well it performs within the context of other outputs. It is key to have both high accuracy and precision and continuously test for methods to improve both in order to be ethically considerate.

Lastly, a key ethical consideration is transparency on the development process as well as the machine translation model itself in order to ensure that the users are able to accurately understand how the model operates. A lack of transparency has ended poorly for a lot of major companies over the years which has led to distrust and critical review of not only the product but the brand itself. By being fully transparent, the decisions made during development as well as the processes in place can be made clear through proper documentation.

**Authors:**

![](assets/image8.png)

For the GitHub screenshot above, archaeme is Francis Dinh, NiTu21 is Nicholas Tubielewicz, pinnouse is Nicholas Wong, YashAgarwal-alt is Yash Agarwal. A link to the detailed view is provided below:

[https://github.com/users/pinnouse/projects/1/views/1](https://github.com/users/pinnouse/projects/1/views/1)

**Task Breakdown**

- Introduction (Nicholas Tubielewicz/Yash Agarwal)
- Model Figure (Nicholas Wong)
- Model Parameters (Yash Agarwal)
- Model Examples (Francis Dinh)
- Data Source (Nicholas Wong)
- Data Summary (Nicholas Wong)
- Data Transformation (Yash Agarwal)
- Data Split (Yash Agarwal)
- Training Curve (Francis Dinh)
- Hyperparameter Tuning (Francis Dinh)
- Quantitative Measures (Nicholas Tubielewicz)
- Quantitative and Qualitative Results (Nicholas Wong)
- Justification of Results (Yash Agarwal)
- Ethical Consideration (Nicholas Tubielewicz/Yash Agarwal)
