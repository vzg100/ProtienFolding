def warn(*args, **kwargs): #Mutes Sklearn warnings
    pass
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import random
from random import randint
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn import svm
from imblearn.ensemble import EasyEnsemble
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import ADASYN
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek
from sklearn.manifold import TSNE
from imblearn.under_sampling import NearMiss
from imblearn.under_sampling import NeighbourhoodCleaningRule
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MaxAbsScaler
import os
from sklearn.metrics import roc_auc_score
import time
from gensim.models import word2vec
from xgboost import XGBClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.svm import OneClassSVM
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import matthews_corrcoef
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer


trash = ["\"", "B", "X", "Z", "U", "X"]


def clean(seq: str, t: list = trash):
    for i in t:
        seq = seq.replace(i, "")
    return seq

def report(results, answers, verbose=0):
    tp, fp, fn, tn = 0, 0, 0, 0
    for i in range(len(results)):
        if results[i] == answers[i]:
            if results[i] == 1:
                tp += 1
            else:
                tn += 1
        elif results[i] != answers[i]:
            if results[i] == 1:
                fp += 1
            else:
                fn += 1
    mcc = matthews_corrcoef(answers, results)
    if tp != 0 and tn != 0 and verbose != 0:
        sen = tp / (tp + fn)  # aka recall aka true positive rate
        spc = tn / (tn+fp)  # specificty or true negative rate
        acc = (tp + tn) / (tp + fp + tn + fn)
        roc = roc_auc_score(answers, results)
        print("Sensitivity:", sen)
        print("Specificity :", spc)
        print("Accuracy:", acc)
        print("ROC", roc)
        print("Matthews Correlation Coeff: ", mcc)
        print("TP", tp, "FP", fp, "TN", tn, "FN", fn)
        print("\n\n")
    else:
        print("Matthews Correlation Coeff: ", mcc)
        print("TP", tp, "FP", fp, "TN", tn, "FN", fn)
        print("\n\n")


def distance(s1: str, s2: str, threshold: float =.9):
    t = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            t += 1
    if ((len(s1)-t) / len(s2)) < threshold:
        return False
    else:
        return True


def windower(sequence: str, position: int, wing_size: int):
    # final window size is wing_size*2 +1
    # Checks to make sure positions and wing_size are not floats
    position = int(position)
    wing_size = int(wing_size)
    # Logic to make sure no errors are thrown due to overhangs when slicing the sequence
    if (position - wing_size) < 0:
        return sequence[:wing_size + position]
    if (position + wing_size) > len(sequence):
        return sequence[position - wing_size:]
    else:
        return sequence[position - wing_size:position + wing_size+1]


def chemical_vector(temp_window: str):
    """
    This provides a feature vector containing the sequences chemical properties
    Currently this contains hydrophobicity (gravy), aromaticity, and isoelectric point
    Overall this vector does not preform well and can act as a control feature vector
    """
    temp_window = clean(temp_window)
    temp_window = ProteinAnalysis(clean(temp_window))
    return [temp_window.gravy(), temp_window.aromaticity(),
            temp_window.isoelectric_point(), temp_window.instability_index()]


# noinspection PyDefaultArgument
def sequence_vector(temp_window: str, window: int = 6, chemical=1):
    """
    This vector takes the sequence and has each amino acid represented by an int
    0 represents nonstandard amino acids or as fluff for tails/heads of sequences
    Strip is a list which can be modified as user needs call for
    """
    temp_window = clean(temp_window)
    temp_window = windower(sequence=temp_window, position=int(len(temp_window)*.5), wing_size=window)

    vec = []
    aa = {"G": 1, "A": 2, "L": 3, "M": 4, "F": 5, "W": 6, "K": 7, "Q": 8, "E": 9, "S": 10, "P": 11, "V": 12, "I": 13,
          "C": 14, "Y": 15, "H": 16, "R": 17, "N": 18, "D": 19, "T": 20, "X": 0}

    for i in temp_window:
        vec.append(aa[i])
    if len(vec) != (window*2)+1:
        t = len(vec)
        for i in range((window*2)+1-t):
            vec.append(0)
    # Hydrophobicity is optional
    if chemical == 1:
        s = ProteinAnalysis(temp_window)
        vec.append(s.gravy())
        vec.append(s.instability_index())
        vec.append(s.aromaticity())

    return vec

def binary_vector(s: str, seq_size: int = 21):
    s = clean(s)
    aa_binary = {
        'A': [0, 0, 0, 0, 0],
        'C': [0, 0, 0, 0, 1],
        'D': [0, 0, 0, 1, 0],
        'E': [0, 0, 0, 1, 1],
        'F': [0, 0, 1, 0, 0],
        'G': [0, 0, 1, 0, 1],
        'H': [0, 0, 1, 1, 0],
        'I': [0, 0, 1, 1, 1],
        'K': [0, 1, 0, 0, 0],
        'L': [0, 1, 0, 0, 1],
        'M': [0, 1, 0, 1, 0],
        'N': [0, 1, 0, 1, 1],
        'P': [0, 1, 1, 0, 0],
        'Q': [0, 1, 1, 0, 1],
        'R': [0, 1, 1, 1, 1],
        'S': [1, 0, 0, 0, 0],
        'T': [1, 0, 0, 0, 1],
        'V': [1, 0, 0, 1, 0],
        'W': [1, 0, 0, 1, 1],
        'Y': [1, 0, 1, 0, 0],
        'ZZ': [1, 1, 1, 1, 1]
    }
    t = [aa_binary[i] for i in s]
    if len(t) < seq_size:
        for i in range(seq_size-len(t)):
            t.append(aa_binary["ZZ"])
    return t


def find_ngrams(s: str, n):
    s = clean(s)
    s = [i for i in s]
    s = [i for i in zip(*[s[i:] for i in range(n)])]
    ngrams = []
    for i in s:
        t = ""
        for j in i:
            t += j
        ngrams.append(t)
    return ngrams


def generate_random_seq(wing_size: int, center: str):
    """
    Generates random sequences and checks that they aren't in locked
    Locked is a list of sequences which are known to be positives
    """
    amino_acids = "GALMFWKQESPVICYHRNDT"
    t1, t2 = "", ""
    for i in range(wing_size):
        t1 += amino_acids[randint(0, 19)]
        t2 += amino_acids[randint(0, 19)]
    final_seq = t1 + center + t2
    return final_seq


class DataCleaner:
    """
    Cleans up data from various csvs with different organizational preferences
    Assumes column names are sequence, code, and position
    Enables the user to generate negative examples, sequences which aren't explicit positives are assumed to negative
    I chose to make the DataCleaner require extra steps to run since I am assuming people using it come from a
    non CS background and
    the extra steps are meant to enable easier debugging and understanding of the flow
    """
    def __init__(self, file: str, delimit: str =",", header_line: int=0, wing=10):
        """

        :param file: Input file
        :param delimit: What delimiter is used by the csv
        :param header_line: Used by pandas to determine the header
        :param wing: how long the seq is on either side of the modified amino acid
        For example wing size of 2 on X would be AAXAA
        """

        self.data = pd.read_csv(file, header=header_line, delimiter=delimit, quoting=3, dtype=object)
        self.protiens = {}
        self.count = 0
        self.labels = []
        self.sequences = []
        self.wing = wing

    def load_data(self, amino_acid: str, aa: str="code", seq: str="sequence", pos: str ="position"):
        """
        Loads the data into the object
        :param amino_acid: Which amino acid is the ptm found on
        :param aa: the column name for the amino acid modified in the PTM site
        :param seq: the column name for the FULL protien sequence
        :param pos: the column name for where the ptm occurs in the PTM,
        Assumed it is 1-based index and the code adjusts for that
        :return: loads data into the data cleaner object
        """
        for i in range(len(self.data[seq])):
            if self.data[aa][i] in amino_acid:
                t = self.data[seq][i]
                try:
                    if t not in self.protiens.keys():
                        self.protiens[t] = [int(self.data[pos][i])]
                    else:
                        self.protiens[t] = self.protiens[t].append(int(self.data[pos][i]))
                except:
                    pass

    def generate_positive(self, window=1):
        """
        Populates the object with the positive PTM sequences, clips them down to the intended size
        :return: Populates the object with the positive PTM sequences
        """

        for i in self.protiens.keys():
            try:
                t = self.protiens[i]
                for j in t:
                    if window == 1:
                        self.sequences.append(windower(sequence=i, position=j-1, wing_size=self.wing))
                        self.labels.append(1)
                    else:
                        try:
                            self.sequences.append(i)
                            self.labels.append(1)
                        except:
                            pass
            except:
                pass

    def generate_negatives(self, amino_acid: str, ratio: int=-1, cross_check: int=-1):
        """
        Finds assumed negatives in the sequences, can control the ratio and whether
        :param amino_acid: The amino acid where the PTM occurs on, used for generating the negative
        :param ratio: if -1 just adds every presumed negative, otherwise use float/int value to determine
        :param cross_check: if -1 doesnt cross check otherwise it ensures
        that no negative sequences extracted match positive sequences
        WARNING: The larger the data the longer it will take
        :return: Adds negatives to data in the object
        """
        self.count = len(list(self.protiens.keys()))
        if ratio < 0:
            for i in self.protiens.keys():
                try:
                    for j in range(len(i)):
                        if i[j] == amino_acid and j+1 not in self.protiens[i]:
                            self.sequences.append(windower(sequence=i, position=j, wing_size=self.wing))
                            self.labels.append(0)
                except:
                    pass
        else:
            t = len(self.sequences)
            for y in range(int(t*ratio)):
                try:
                    for i in self.protiens.keys():
                        for j in range(len(i)):
                            if i[j] == amino_acid and j + 1 not in self.protiens[i]:
                                s = windower(sequence=i, position=j, wing_size=self.wing)
                                if cross_check < 0:
                                    self.sequences.append(s)
                                    self.labels.append(0)
                                else:
                                    for subsequence in self.sequences:
                                        if not distance(s1=subsequence, s2=s):
                                            self.sequences.append(s)
                                            self.labels.append(0)
                except:
                    pass

    def write_data(self, output: str, seq_col: str="sequence", label_col: str="label", shuffle=0):
        """
        Writes the data to an output file
        :param output: Output file name
        :param seq_col: column name of the sequence
        :param label_col: Column of the label of the classifier
        :param shuffle: If not 0 will randomly shuffle the data before writing it
        :return:
        """
        file = open(output, "w+")
        t = str(seq_col) + "," + str(label_col)+"\n"
        file.write(t)
        if shuffle != 0:
            temp = list(zip(self.sequences, self.labels))
            random.shuffle(temp)
            self.sequences, self.labels = zip(*temp)
        for i in range(len(self.sequences)):
            file.write(str(self.sequences[i]) + "," + str(self.labels[i]) + "\n")

    def generate_corpus(self, num_features: int=300, min_word_count: int=1, num_workers: int=4, downsampling=1e-3,
                        context=10):
        self.words = []
        for i in self.protiens.keys():
            self.words.append(i.split())
        num_features = num_features  # Word vector dimensionality
        min_word_count = min_word_count  # Minimum word count
        num_workers = num_workers  # Number of threads to run in parallel
        context = context  # Context window size
        downsampling = downsampling
        self.model = word2vec.Word2Vec(self.words, workers=num_workers, size=num_features, min_count = min_word_count,
                                       window=context, sample=downsampling)
        self.model.init_sims(replace=True)


class FastaToCSV:
    # More Benchmarks
    def __init__(self, negative: str, positive: str, output: str):
        write_head = 0
        if not os.path.isfile(output):
            write_head = 1
        output = open(output, "a+")
        if write_head == 1:
            output.write("sequence,label,code\n")
        negative = open(negative)
        for line in negative:
            if ">" not in line:
                line = line.replace("\n", "")
                s = line+","+str(0)+","+line[10]+"\n"
                output.write(s)
        negative.close()
        positive = open(positive)
        for line in positive:
            line = line.replace("\n", "")
            if ">" not in line:
                s = line+","+str(1)+","+line[10]+"\n"
                output.write(s)
        positive.close()
        output.close()


class DataDict:
    def __init__(self, file, delimit=",", header_line=0, seq="sequence", pos="label"):
        self.data = {}
        self.seq = seq
        self.pos = pos
        data = pd.read_csv(file, header=header_line, delimiter=delimit, quoting=3, dtype=object, error_bad_lines=False)
        data = data.reindex(np.random.permutation(data.index))
        for i in range(len(data[self.seq])):
            if type(data[self.seq][i]) == str:
                self.data[data[self.seq][i]] = int(data[self.pos][i])

    def out_put(self,):
        f = []
        l = []
        for i in self.data.keys():
            f.append(i)
            if self.data[i] == 1:
                l.append(1)
            else:
                l.append(0)
        return f, l

    def add_seq(self, seq: str, label: int):
        try:
            self.data[seq] = label
        except:
            print("Sequence Already Present")
            pass

    def check(self, seq: str):
        if seq not in self.data.keys():
            return 1
        else:
            return -1


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class Predictor:
    """
    The prototyping tool, meant to work with data outputted by datacleaner

    """
    def __init__(self,  window_size=6, training_ratio=.7, seq="sequence", pos="label"):
        self.training_ratio = training_ratio  # Float value representing % of data used for training
        self.features = []
        self.labels = []
        self.words = []
        self.window_size = window_size
        self.supervised_classifiers = {"forest": RandomForestClassifier(n_jobs=4),
                                       "mlp_adam": MLPClassifier(),
                                       "svc": svm.SVC(verbose=1),
                                       "xgb": XGBClassifier(max_delta_step=5),
                                       "bagging": BaggingClassifier(), "one_class_svm": OneClassSVM(kernel="rbf")
                                       }

        self.imbalance_functions = {"easy_ensemble": EasyEnsemble(), "SMOTEENN": SMOTEENN(),
                                    "SMOTETomek": SMOTETomek(), "ADASYN": ADASYN(),
                                    "random_under_sample": RandomUnderSampler(), "ncl": NeighbourhoodCleaningRule(),
                                    "near_miss": NearMiss(), "pass": -1}
        self.seq = seq
        self.pos = pos
        self.random_data = 0
        self.test_results = 0
        self.vecs = {"sequence": sequence_vector, "chemical": chemical_vector, "binary": binary_vector, "w2v": "w2v"}
        self.vector = 0
        self.features_labels = {}
        self.test_cv = 0
        self.benchmark_mcc = 0
        self.mcc_scorer = make_scorer(matthews_corrcoef)
    def load_data(self, file, delimit=",", header_line=0):
        """
        Reads the data for processing
        :param file: File name
        :param delimit: for pandas
        :param header_line: for pandas
        :return: Loads the data inot the object
        """
        # Modify these if working with different CSV column names
        print("Loading Data")
        self.data = DataDict(file=file, delimit=delimit, header_line=header_line)
        print("Loaded Data")

    def process_data(self, imbalance_function, amino_acid: str, vector_function: str, random_data=-1, ratio: int=1):
        """
        Handles much of the data processing
        :param imbalance_function: str which is passed through dict to apply imbalanced functions to the data
        :param amino_acid: Amino acid of focus TODO: move to init
        :param vector_function: Function under which data is vectorized
        :param random_data: Flag on whether to use random data, by default selected
        :param ratio: desired ratio of random data to real data
        :return:
        """
        self.random_data = random_data
        print("Working on Data")
        self.vector = self.vecs[vector_function]
        self.features, self.labels = self.data.out_put()
        if self.random_data == 1:
            self.random_seq = []
            for i in range(int(ratio * len(self.features))):
                self.random_seq.append(generate_random_seq(center=amino_acid, wing_size=int(self.window_size * .5)))
        if type(self.random_data) == str:
            f = open(self.random_data)
            key = [line for line in f]
            self.random_seq = []
            for i in range(int(ratio * len(self.features))):
                s = generate_random_seq(center=amino_acid, wing_size=int(self.window_size * .5))
                if s not in key:
                    self.random_seq.append(s)
        self.features = list(map(self.vector, self.features))
        self.features = list(self.features)
        for i in self.features:
            if len(i) != 16:
                print(i)
        print("Sample Vector", self.features[randint(0, len(self.features)-1)])
        temp = list(zip(self.features, self.labels))
        random.shuffle(temp)
        self.features, self.labels = zip(*temp)
        if self.imbalance_functions[imbalance_function] != -1:
            print("Balancing Data")
            imba = self.imbalance_functions[imbalance_function]
            self.features, self.labels = imba.fit_sample(self.features, self.labels)
            print("Balanced Data")
        print("Finished working with Data")

    def supervised_training(self, classy: str, scale: str =-1, break_point: int = 3200, test_size=.2, params={}):
        """
        Trains and tests the classifier on the data
        :param classy: Classifier of choice, is string passed through dict
        :param scale: Applies a scaler function from sklearn if not -1
        :param break_point: how many seconds till negative random data samples will stop being generated
        :return: Classifier trained and ready to go and some results
        """
        if params == {}:
            self.classifier = self.supervised_classifiers[classy]
        else:
            self.classifier = RandomizedSearchCV(self.supervised_classifiers[classy], param_distributions=params)
        self.scale = scale
        check = 12
        while check != 0:
            self.X_train, self.X_test, self.y_train, self.y_test = \
                train_test_split(self.features, self.labels, test_size=test_size, random_state=check)
            if 1 in self.y_test and 1 in self.y_train:
                check = 0
            else:
                print("Reshuffling, no positive samples in either y_test or y_train ")
                check += 1
        c = 0
        if self.random_data > 1 or type(self.random_data) == str:
            t = time.time()
            print("Random Sequences Generated", len(self.random_seq))
            print("Filtering Random Data")
            self.X_train = list(self.X_train)
            self.y_train = list(self.y_train)
            for i in self.random_seq:
                if break_point == -1:
                    pass
                elif time.time() - t > break_point:
                    print("Timing out Random Data incorperation into test Data")
                    break
                if self.data.check(i) == 1:
                    self.X_train.append(self.vector(i))
                    self.y_train.append(0)
                    c += 1
            self.X_train = np.asarray(self.X_train)
            self.y_train = np.asarray(self.y_train)
            print("Random Data Added:", c)
            print("Finished with Random Data")
        print("Training Data Points:", len(self.X_train))
        print("Test Data Points:", len(self.X_test))
        if self.scale != -1:
            print("Scaling Data")
            st = {"standard": StandardScaler(), "robust": RobustScaler(),
                  "minmax": MinMaxScaler(), "max": MaxAbsScaler()}
            self.X_train = st[scale].fit_transform(X=self.X_train)
            self.X_test = st[scale].fit_transform(X=self.X_test)
            print("Finished Scaling Data")
        print("Starting Training")
        self.X_train = np.asarray(self.X_train)
        self.y_train = np.asarray(self.y_train)

        self.classifier.fit(self.X_train, self.y_train)
        print("Done training")
        self.test_results = self.classifier.predict(self.X_test)
        print("Test Results")
        print(report(answers=self.y_test, results=self.test_results))
        self.test_cv = cross_val_score(self.classifier, np.asarray(self.features), np.asarray(self.labels), cv=10, scoring=self.mcc_scorer).mean()
        print("Cross Validation:",self.test_cv )

    def benchmark(self, benchmark: str, aa: str, window=13):
        benchmark = open(benchmark)
        validation = []
        answer_key = []
        for i in benchmark:
            s = i.split(",")
            label = s[1].replace("\n", "").replace("\t", "")
            seq = s[0].replace("\n", "").replace("\t", "")
            code = s[2].replace("\n", "").replace("\t", "")
            seq = windower(sequence=seq, wing_size=self.window_size, position=int(len(seq) * .5))
            if aa == code:
                validation.append(self.vector(seq))
                answer_key.append(int(label))
        print("Number of data points in benchmark", len(validation))
        print("Sample Vector", validation[0])
        validation = np.asarray(validation)
        if self.scale != -1:
            print("Scaling Data")
            st = {"standard": StandardScaler(), "robust": RobustScaler(),
                  "minmax": MinMaxScaler(), "max": MaxAbsScaler()}
            validation = st[self.scale].fit_transform(X=validation)
        v = self.classifier.predict(np.asarray(validation))
        v.reshape(len(v), 1)
        answer_key = np.asarray(answer_key)
        answer_key.reshape(len(answer_key), 1)

        t = []
        for i in v:
            t.append(int(i))
        v = np.asarray(t).reshape(len(t), 1)
        for i in range(len(answer_key)):
            if answer_key[i] != 0 and answer_key[i] != 1:
                print(i, "answer")
            if v[i] != 0 and v[i] != 1:
                print(i, "V", v[i], type(v[i]))
        self.benchmark_mcc = matthews_corrcoef(answer_key, v)

        print("Benchmark Results ")
        print(report(answers=answer_key, results=v))

    def generate_pca(self):
        """
        :return: PCA of data
        """
        y = np.arange(len(self.features))
        pca = PCA(n_components=2)
        x_np = np.asarray(self.features)
        pca.fit(x_np)
        X_reduced = pca.transform(x_np)
        plt.figure(figsize=(10, 8))
        plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=y, cmap='RdBu', s=1)
        plt.xlabel('First component')
        plt.ylabel('Second component')
        plt.show()

    def generate_tsne(self):
        y = np.arange(len(self.features))
        tsne = TSNE(n_components=2)
        x_np = np.asarray(self.features)
        X_reduced = tsne.fit_transform(x_np)
        plt.figure(figsize=(10, 8))
        plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=y, cmap='RdBu', s=1)
        plt.xlabel('First component')
        plt.ylabel('Second component')
        plt.show()

    def test_seq(self, s: str):
        s = self.vector(s)
        return self.classifier.predict(s)

    def test_sequences(self, s: list):
        t = []
        for i in s:
            t.append(self.vector(i))
        return self.classifier.predict(t)
