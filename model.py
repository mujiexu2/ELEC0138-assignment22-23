import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
import torch.backends.cudnn as cudnn


class TextCNN(torch.nn.Module):
    def __init__(self, vocab_size, embedding_size, num_classes, kernel_sizes, num_kernels):
        super(TextCNN, self).__init__()
        self.embedding = torch.nn.Embedding(vocab_size, embedding_size)
        self.convs = torch.nn.ModuleList(
            [torch.nn.Conv2d(1, num_kernels, (K, embedding_size)) for K in kernel_sizes])
        self.dropout = torch.nn.Dropout(0.5)
        self.fc = torch.nn.Linear(len(kernel_sizes) * num_kernels, num_classes)

    def forward(self, x):
        x = self.embedding(x)  # [batch_size, sequence_length, embedding_size]
        x = x.unsqueeze(1)  # [batch_size, 1, sequence_length, embedding_size]
        x = [torch.nn.functional.relu(conv(x)).squeeze(3) for conv in self.convs]  # [batch_size, num_kernels, sequence_length - kernel_size + 1] * len(kernel_sizes)
        x = [torch.nn.functional.max_pool1d(i, i.size(2)).squeeze(2) for i in x]  # [batch_size, num_kernels] * len(kernel_sizes)
        x = torch.cat(x, 1) # [batch_size, num_kernels * len(kernel_sizes)]
        x = self.dropout(x)  # (N, len(Ks)*Co)
        logit = self.fc(x)  # (N, C)
        return logit

def data2char_index(data, max_len):
    alphabet = " abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+-=<>()[]{}"
    mat = []
    for ch in data:
        if ch not in alphabet:
            continue
        mat.append(alphabet.index(ch))
    if len(mat) < max_len:
        mat += [0] * (max_len - len(mat))
    elif len(mat) > max_len:
        mat = mat[:max_len]
    return mat


#@Param String sentence: the sentence to be predicted
def modelService(sentence):

    """"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    sentence_flask = sentence
    max_len = 1000
#Preprocess the sentence
    processed_sentence_flask = data2char_index(sentence_flask, max_len)

#Torched the sentence
    torched_sentence_flask = torch.tensor(processed_sentence_flask)
    model = torch.load('checkpoint_textcnn.pth.tar')['model'].to(device)
    model.eval()
    data = torched_sentence_flask.unsqueeze(0).to(device)
    #TODO: format the output, label
    output = model(data).argmax(dim=1).cpu()
    return output

# input_sentence = """<li><a href="/wiki/File:Socrates.png" class="image"><img alt="Socrates.png" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/18px-Socrates.png" decoding="async" width="18" height="28" class="noviewer" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/27px-Socrates.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/36px-Socrates.png 2x" data-file-width="326" data-file-height="500" /> </a> <a href="/wiki/Portal:Philosophy" title="Portal:Philosophy">Philosophy&#32;portal </a> </li> </ul>"""
# #<li><a href="/wiki/File:Socrates.png" class="image"><img alt="Socrates.png" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/18px-Socrates.png" decoding="async" width="18" height="28" class="noviewer" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/27px-Socrates.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/36px-Socrates.png 2x" data-file-width="326" data-file-height="500" /> </a> <a href="/wiki/Portal:Philosophy" title="Portal:Philosophy">Philosophy&#32;portal </a> </li> </ul><li><a href="/wiki/File:Socrates.png" class="image"><img alt="Socrates.png" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/18px-Socrates.png" decoding="async" width="18" height="28" class="noviewer" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/27px-Socrates.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Socrates.png/36px-Socrates.png 2x" data-file-width="326" data-file-height="500" /> </a> <a href="/wiki/Portal:Philosophy" title="Portal:Philosophy">Philosophy&#32;portal </a> </li> </ul>
# modelService(input_sentence)