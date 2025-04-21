import os
from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from .forms import EncryptForm, DecryptForm
from .utils import TripathiBuffer
from PIL import Image
import numpy as np
from PIL import ImageOps


def index(request):
    return render(request, 'tbuffer_app/index.html')

def encrypt_view(request):
    if request.method=='POST':
        form = EncryptForm(request.POST, request.FILES)
        if form.is_valid():
            #img = Image.open(form.cleaned_data['image'])
            raw = Image.open(form.cleaned_data['image'])
            img = ImageOps.exif_transpose(raw).convert('RGB')
            key = form.cleaned_data['secret_key']
            noisy, noise, composite = TripathiBuffer.encrypt(img, key)

            enc_path   = f"media/enc_{request.FILES['image'].name}"
            noise_path = f"media/noise_{request.FILES['image'].name}"
            key_path   = f"media/key_{request.FILES['image'].name}.tkey"
            Image.fromarray(noisy).save(enc_path)
            Image.fromarray(noise).save(noise_path)
            with open(key_path,'w') as f: f.write(composite)

            return render(request,'tbuffer_app/result.html',{
              'enc_url':   enc_path.replace('media/','/media/'),
              'noise_url': noise_path.replace('media/','/media/'),
              'key_url':   key_path.replace('media/','/media/')
            })
    else:
        form = EncryptForm()
    return render(request,'tbuffer_app/index.html', {'encrypt_form': form})

def decrypt_view(request):
    if request.method=='POST':
        form = DecryptForm(request.POST, request.FILES)
        if form.is_valid():
            raw = Image.open(form.cleaned_data['image'])
            enc_img = ImageOps.exif_transpose(raw).convert('RGB')
            raw = request.FILES['key_file'].read().decode()
            skey = form.cleaned_data['secret_key']
            arr = np.array(enc_img)
            try:
                rec = TripathiBuffer.decrypt(arr, raw, skey)
            except Exception as e:
                return HttpResponse(f"Error: {e}", status=400)
            out_path = f"media/rec_{request.FILES['image'].name}"
            Image.fromarray(rec).save(out_path)
            return render(request,'tbuffer_app/result.html',{
              'rec_url': out_path.replace('media/','/media/')
            })
    else:
        form = DecryptForm()
    return render(request,'tbuffer_app/index.html', {'decrypt_form': form})
