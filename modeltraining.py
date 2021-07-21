import warnings

import numpy as np
from onnxruntime.capi.onnxruntime_inference_collection import InferenceSession
import skl2onnx
from scipy.io.wavfile import read
from sklearn.mixture import GaussianMixture

from featureextraction import extract_features

warnings.filterwarnings("ignore")

# path to training data
# source   = "development_set/"
source = "trainingData/"

# path where training speakers will be saved

# dest = "speaker_models/"
# train_file = "development_set_enroll.txt"

dest = "Speakers_models/"
#train_file = "trainingDataPath.txt"
train_file = "ourTraining.txt"
file_paths = open(train_file, 'r')

count = 1
# Extracting features for each speaker (5 files per speakers)
features = np.asarray(())
for path in file_paths:
    #readfile
    path: str = path.strip()
    print(path)

    # read the audio
    sr, audio = read(source + path)

    # extract 40 dimensional MFCC & delta MFCC features
    # #featureextraction.py需要去理解MFCC之運作
    vector = extract_features(audio, sr)

    if features.size == 0:
        features = vector
    else:
        features = np.vstack((features, vector))
    # when features of 5 files of speaker are concatenated, then do model training
    # -> if count == 5: --> edited below
    #print(count)
    if count == 5:
        print(features.shape)
        print(features[:1].shape)

        gmm = GaussianMixture(n_components=16,
                              max_iter=200,
                              covariance_type='diag',
                              n_init=3)
        gmm.fit(features)

        # serialize to onnx
        onx = skl2onnx.to_onnx(model=gmm,
                               X=features[:1].astype(np.float32),
                               target_opset=13,
                               options={"score_samples": True})
        onx_filename = path.split("-")[0] + (".onnx")
        print(onx_filename)
        with open(onx_filename, "wb") as file:
            file.write(onx.SerializeToString())

        # verify onnx model correctness
        # run with sklearn
        sk_prob_output: np.ndarray = gmm.predict_proba(features[:1])
        # run with onnx
        sess = InferenceSession(onx.SerializeToString())
        sess_prob_output: np.ndarray = sess.run(
            None, {'X': features[:1].astype(np.float32)})[1]
        # calculate output difference
        sk_prob_output_flatten: np.ndarray = sk_prob_output.ravel()
        sess_prob_output_flatten: np.ndarray = sess_prob_output.ravel()
        diff: np.ndarray = np.abs(sk_prob_output_flatten -
                                  sess_prob_output_flatten)
        print(
            str.format("difference between sklearn output and onnx output = {}",
                       diff.mean()))

        # dumping the trained gaussian model#picklefile用於python特有的型別和python的資料型別間進行轉換
        # picklefile = path.split("-")[0] + (".onnx")
        # pickle.dump(gmm, open(dest + picklefile, 'wb'))
        # print(('+ modeling completed for speaker:', picklefile, " with data point = ", features.shape))
        features = np.asarray(())
        count = 0
    count = count + 1