# -*- coding: utf-8 -*-
"""CSC413_FP_Training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/pinnouse/zeroshot-unsurpervised-mt/blob/main/CSC413_FP_Training.ipynb

## Train Loop

PyTorch training for GAN:
[PyTorch blog](https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html)
"""
from models import Decoder, Transformer, Translator, Discriminator
from data_loader import tokenizer, device
from typing import List

print(tokenizer.vocab_size)
real_decoder = Decoder(tokenizer.vocab_size)
transformer = Transformer(tokenizer.vocab_size) # temp vocab size
translate = Translator(hidden=512)
discriminator = Discriminator()

real_decoder.to(device)
transformer.to(device)
translate.to(device)
discriminator.to(device)

from torch import optim
# https://huggingface.co/docs/transformers/main_classes/optimizer_schedules#transformers.Adafactor
from transformers.optimization import Adafactor
import matplotlib.pyplot as plt
from datetime import datetime
from google.colab import drive

context_length = 64

# TODO: add device specific code

def pad(tokens, context_length):
  l = list(tokens)
  for _ in range(context_length - len(tokens)):
    l.append(tokenizer.pad_token_id)
  return np.array(l)

def plot_loss(title: str, losses: List[float]) -> None:
  plt.title(title)
  plt.plot(losses)
  plt.show()

def train_decoder(real_decoder, real_train, data_loader, device='cpu', epochs=10, batch_size=256):
  criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
  r_optim = Adafactor(real_decoder.parameters())
  n = len(real_train) // batch_size
  r_losses = []

  for e in range(epochs):
    r_epoch_loss = 0
    for i, (r_x, _) in enumerate(data_loader):
      if (i + 1) % 100 == 0:
        print(f'Iteration {i+1} of {n}')
      
      rx_clips = torch.tensor(np.array(list(map(lambda x: x[1], r_x))), device=device)
      rx_toks = torch.tensor(np.array(list(map(lambda x: x[2].numpy(force=True), r_x))), device=device)
      
      r_epoch_loss += train_decoder_iteration(real_decoder, device, criterion, rx_clips, rx_toks, r_optim)
    
    r_losses.append(r_epoch_loss)
  
  # Show loss graph
  plot_loss('Decoder Loss', r_losses)

def train_decoder_iteration(real_decoder, device, criterion, rx_clips, rx_toks, r_optim):
  '''
  Perform one iteration of training a decoder and return the loss of the decoder.
  '''
  tgt_in = rx_toks[:, :-1]
  tgt_expect = rx_toks[:, 1:]
  r_mask = nn.Transformer.generate_square_subsequent_mask(context_length - 1, device=device)
  r_output = real_decoder(rx_clips, tgt_in, tgt_mask=r_mask)
  r_output = r_output.permute(0,2,1)
  r_loss = criterion(r_output, tgt_expect)

  r_optim.zero_grad()
  r_loss.backward(retain_graph=True)
  r_optim.step()

  return r_loss.item()


def train_transformer(transformer, other_train, data_loader, device='cpu', epochs=10, batch_size=256):
  criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
  g_optim = Adafactor(real_decoder.parameters())
  n = len(other_train) // batch_size
  g_losses = []

  for e in range(epochs):
    g_epoch_loss = 0
    for i, (_, o_x) in enumerate(data_loader):
      if (i + 1) % 100 == 0:
        print(f'Iteration {i+1} of {n}')
      
      ox_toks = torch.tensor(np.array(list(map(lambda x: x[1].numpy(force=True), o_x))), device=device)
      _, g_loss = train_transformer_iteration(transformer, device, criterion, g_optim, ox_toks)
      g_epoch_loss += g_loss
    g_losses.append(g_epoch_loss)
  
  plot_loss('Transformer Loss', g_losses)

def train_transformer_iteration(transformer, device, criterion, g_optim, ox_toks):
  '''
  Perform one iteration of training a transformer and return both the resulting embeddings and the loss of the transformer.
  Based on: https://jamesmccaffrey.wordpress.com/2022/09/09/simplest-transformer-seq-to-seq-example/
  '''
  src = ox_toks
  tgt = src
  tgt_in = tgt[:,:-1]
  tgt_expect = tgt[:,1:]
  t_mask = nn.Transformer.generate_square_subsequent_mask(context_length - 1, device=device)
  # https://pytorch.org/tutorials/beginner/translation_transformer.html#seq2seq-network-using-transformer
  tgt_attn_mask = (tgt_in == tokenizer.pad_token_id)
  attn_mask = (src == tokenizer.pad_token_id)

  output, other_embeddings = transformer(src, tgt_in, tgt_mask=t_mask, tp_mask=tgt_attn_mask, sp_mask=attn_mask) # [bs,seq,vocab]

  # get preds shape to conform to tgt_expect
  output = output.permute(0,2,1)  # now [bs, vocab, seq]

  g_loss = criterion(output, tgt_expect)

  g_optim.zero_grad()
  g_loss.backward(retain_graph=True)
  g_optim.step()
  return other_embeddings, g_loss.item()

def train_discriminator(discriminator, other_embeddings, real_train, other_train, data_loader, device='cpu', epochs=10, batch_size=256):
  criterion_binary = nn.BCEWithLogitsLoss()
  d_optim = Adafactor(discriminator.parameters())
  d_losses = []

  r_iterations = len(real_train) // batch_size
  o_iterations = len(other_train) // batch_size
  # r_iterations = real_train.shape[0] // batch_size
  # o_iterations = other_train.shape[0] // batch_size

  n = min(r_iterations, o_iterations)
  for e in range(epochs):
    d_epoch_loss = 0
    for i, (r_x, o_x) in enumerate(data_loader):
      if (i + 1) % 100 == 0:
        print(f'Iteration {i+1} of {n}')
      _, _, _, d_loss = train_discriminator_iteration(discriminator, translate, device, criterion_binary, d_optim, r_x, o_x, other_embeddings)
      d_epoch_loss += d_loss
    
    d_losses.append(d_epoch_loss)
  
  plot_loss('Discriminator Loss', d_losses)


def train_discriminator_iteration(discriminator, translate, device, criterion_binary, d_optim, r_x, o_x, other_embeddings):
  rx_clips = torch.tensor(np.array(list(map(lambda x: x[1], r_x))), device=device)
  n_r = len(r_x)
  n_o = len(o_x)
  fake_embs, F_embs = translate(other_embeddings[:,-1,:])
  real_embs = rx_clips[:,-1,:]
  inputs = torch.cat([real_embs, fake_embs])
  reals = torch.ones(n_r, device=device) #whatever batch_sizes will be
  fakes = torch.zeros(n_o, device=device) # ^^
  labels = torch.cat([reals,fakes]) #[n_1 + n_2,512]

  d_outputs = discriminator(inputs) 
  d_loss = criterion_binary(d_outputs, labels)
  d_optim.zero_grad()
  d_loss.backward(retain_graph=True)
  d_optim.step()
  return fake_embs,F_embs,fakes,d_loss.item()


def train_translator(translator, data_loader, other_embeddings, fake_embs, F_embs, fakes, epochs=10, batch_size=256):
  criterion_binary = nn.BCEWithLogitsLoss()
  mse = nn.MSELoss()
  t_optim = Adafactor(translate.parameters())
  t_losses = []

  r_iterations = len(real_train) // batch_size
  o_iterations = len(other_train) // batch_size
  # r_iterations = real_train.shape[0] // batch_size
  # o_iterations = other_train.shape[0] // batch_size
  n = min(r_iterations, o_iterations)
  for e in range(epochs):
    t_epoch_loss = 0
    for i, (r_x, o_x) in enumerate(data_loader):
      if (i + 1) % 100 == 0:
        print(f'Iteration {i+1} of {n}')
      t_epoch_loss += train_trainslator_iteration(discriminator, criterion_binary, mse, t_optim, other_embeddings, fake_embs, F_embs, fakes)
    t_losses.append(t_epoch_loss)
  
  plot_loss('Translator Loss', t_losses)

def train_trainslator_iteration(discriminator, criterion_binary, mse, t_optim, other_embeddings, fake_embs, F_embs, fakes):
  t_outputs = discriminator(fake_embs)
  t_loss = criterion_binary(t_outputs, fakes)
  tl_loss = mse(F_embs, other_embeddings[:,-1,:]) # "cycle GAN" reconstruct fr embeddings
  t_optim.zero_grad()
  t_loss.backward(retain_graph=True)
  tl_loss.backward()
  t_optim.step()

  return t_loss.item()

def train(real_decoder, transformer, discriminator, translate, # our four models
          real_train, other_train, real_valid = None, other_valid = None, device = 'cpu',
          epochs = 10, batch_size = 256, ckpt_path = None, ckpt_interval = 10):
  batch_data = []

  # yash
  data_loader = [(real_train, other_train)]

  criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
  criterion_binary = nn.BCEWithLogitsLoss()
  mse = nn.MSELoss()

  # r_optim = optim.RAdam(real_decoder.parameters())
  # g_optim = optim.RAdam(generator.parameters())
  r_optim = Adafactor(real_decoder.parameters())
  g_optim = Adafactor(transformer.parameters())
  t_optim = Adafactor(translate.parameters())
  d_optim = Adafactor(discriminator.parameters())

  r_iterations = len(real_train) // batch_size
  o_iterations = len(other_train) // batch_size
  # r_iterations = real_train.shape[0] // batch_size
  # o_iterations = other_train.shape[0] // batch_size

  n = min(r_iterations, o_iterations)

  r_losses = []
  g_losses = []
  t_losses = []
  d_losses = []

  for e in range(epochs):
    r_epoch_loss = 0
    g_epoch_loss = 0
    d_epoch_loss = 0
    t_epoch_loss = 0
    # yash (every epoch: shuffle)
    # data_loader = batcherize(train_data)
    # data_loader.shuffle()
    # random.shuffle(batches of the dataloader)
    epoch_start = datetime.now()
    print(f'Epoch {e+1}:')
    for i, (r_x, o_x) in enumerate(data_loader):
      # r_x: (english sentence: str, CLIP embeddings: float[512], tokens: one-hots[num tokens])[batch_size]
      # o_x: (fr sentence: str, tokens: one-hot[num tokens])[batch_size]
      # if r_x.shape[0] < batch_size: # not full batch
      #   break
      if (i + 1) % 100 == 0:
        print(f'Iteration {i+1} of {n}')
      
      rx_clips = torch.tensor(np.array(list(map(lambda x: x[1], r_x))), device=device)
      rx_toks = torch.tensor(np.array(list(map(lambda x: x[2].numpy(force=True), r_x))), device=device)
      ox_toks = torch.tensor(np.array(list(map(lambda x: x[1].numpy(force=True), o_x))), device=device)
      
      # ==============================
      # == learn decoder
      # ==============================
      
      r_epoch_loss += train_decoder_iteration(real_decoder, device, criterion, rx_clips, rx_toks, r_optim)

      # ==============================
      # == self learn monolingual
      # ==============================
      # "other" generator self supervised
      # https://jamesmccaffrey.wordpress.com/2022/09/09/simplest-transformer-seq-to-seq-example/
      other_embeddings, g_loss = train_transformer_iteration(transformer, device, criterion, g_optim, ox_toks)
      g_epoch_loss += g_loss

      # ==============================
      # == learn discriminator
      # ==============================
      fake_embs, F_embs, fakes, d_loss = train_discriminator_iteration(discriminator, translate, device, criterion_binary, d_optim, r_x, o_x, other_embeddings)
      d_epoch_loss += d_loss

      # ==============================
      # == learn translator
      # ==============================
      t_epoch_loss += train_trainslator_iteration(discriminator, criterion_binary, mse, t_optim, other_embeddings, fake_embs, F_embs, fakes)


    print(f'\ttrain loss (decoder)   : {r_epoch_loss}')
    print(f'\ttrain loss (generator) : {g_epoch_loss}')
    print(f'\ttrain loss (discrim)   : {d_epoch_loss}')
    print(f'\ttrain loss (translator): {t_epoch_loss}')
    print(f'\ttook: {(datetime.now() - epoch_start).total_seconds()} seconds')
    r_losses.append(r_epoch_loss)
    g_losses.append(g_epoch_loss)
    d_losses.append(d_epoch_loss)
    t_losses.append(t_epoch_loss)
    if ckpt_path is not None and e % ckpt_interval == 0:
      state = {
          'real_decoder_state': real_decoder.state_dict(),
          'real_decoder_loss': r_epoch_loss,
          'transformer_state': transformer.state_dict(),
          'transformer_loss': t_epoch_loss,
          'discriminator_state': discriminator.state_dict(),
          'discriminator_loss': d_epoch_loss,
          'translate_state': translate.state_dict(),
          'translate_loss': t_epoch_loss,
      }
      torch.save(state, ckpt_path + f'/ckpt-epoch-{e}.pt')
  plot_loss('Decoder Loss', r_losses)
  plot_loss('Transformer Loss', g_losses)
  plot_loss('Discriminator Loss', d_losses)
  plot_loss('Translator Loss', t_losses)
  

print(train_data_fr[0])
# To disable checkpointing, comment the next two lines and remove the ckpt_path
# parameter in the call to train().
drive.mount('/content/gdrive')
ckpt_path = '/content/gdrive/My Drive/CSC413/Project/'
train(real_decoder, transformer, discriminator, translate, [train_data_en[0]] * 2, [train_data_fr[0]] * 16, epochs=100, device=device, ckpt_path=ckpt_path)
# train(real_decoder, transformer, discriminator, translate, train_data_en, train_data_fr, epochs=100, ckpt_path=ckpt_path)

"""### Overfit Inference"""

from google.colab import drive
drive.mount('/content/gdrive')
ckpt_path = '/content/gdrive/My Drive/CSC413/Project/ckpt-epoch-90.pt'
checkpoint = torch.load(ckpt_path)

real_decoder.load_state_dict(checkpoint['real_decoder_state'])
transformer.load_state_dict(checkpoint['transformer_state'])
translate.load_state_dict(checkpoint['translate_state'])
# discriminator.load_state_dict(checkpoint['discriminator'])

real_decoder.eval()
transformer.eval()
translate.eval()

x = train_data_fr[0]
print(f'input: {x}')
xx = torch.tensor(np.array([x[1].numpy()]))
sp = (xx == tokenizer.pad_token_id)
embs = transformer.encode(xx, sp_mask=sp)
en_embs, _ = translate(embs[:,-1:])

print('='*26)
s = [tokenizer.cls_token_id]
for i in range(30):
  seq = torch.tensor(np.array([s]))
  t_mask = nn.Transformer.generate_square_subsequent_mask(i + 1)
  o = real_decoder(en_embs[:,-1:], seq, t_mask)
  m = torch.argmax(o, dim=2)
  tk = m[0, -1]
  s.append(tk)
  print(tokenizer.decode(s))
  if tk == tokenizer.eos_token_id:
    break
