# -*- coding: utf-8 -*-

"""
Copyright (C) 2008 GestorPsi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import os
from django.http import HttpResponse  
from gestorpsi.settings import MEDIA_ROOT
import uuid
from PIL import Image
from gestorpsi.util.decorators import permission_required_with_403
from gestorpsi.referral.models import ReferralAttach, Referral, REFERRAL_ATTACH_TYPE
from gestorpsi.client.models import Client
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

@permission_required_with_403('upload.upload_write')
def send(request):
    if request.method == 'POST':
        user = request.user
        filename = ''
        if 'file' in request.FILES:
            pathdir = '%simg/organization/%s' % (MEDIA_ROOT, user.get_profile().org_active.id)
            if not os.path.exists(pathdir):
                os.mkdir(pathdir)
                os.mkdir('%s/.thumb' % pathdir)
                os.mkdir('%s/.thumb-whitebg' % pathdir)
                os.chmod(pathdir, 0777)
                os.chmod('%s/.thumb' % pathdir, 0777)
                os.chmod('%s/.thumb-whitebg' % pathdir, 0777)
            file = request.FILES['file']

            try:
                if file.content_type in ['image/jpeg', 'image/png', 'image/gif']:
                    filename = str(uuid.uuid4()) + '.png'
                    destination = open('%s/%s' % (pathdir,  filename), 'w+')
                    for chunk in file.chunks():
                        destination.write(chunk)
                    destination.close()
                    im = Image.open('%s/%s' % (pathdir,  filename))
                    im.save('%s/%s' % (pathdir,  filename), "PNG")
    
                    # thumbnail 
                    img = Image.open('%s/%s' % (pathdir, filename))
                    size = img.size
                    
                    w = float(size[0])
                    h = float(size[1])
                   
                    if h/w < 1.155172414: # width > height
                        h = float(116) * h/w
                        w = 116
                    else:
                        w = float(134) * h/w
                        h = 134

                    img.thumbnail((int(w),int(h)), Image.ANTIALIAS)
                    
                    # put background
                    bg = Image.new('RGBA',(116,134), (0,0,0,0)) # transparent
                    bg_white = Image.new('RGBA',(116,134), (255,255,255,255)) # white
                    W, H = bg.size
                    w, h = img.size
                    xo, yo = (W-w)/2, (H-h)/2
                    
                    # merge it
                    bg.paste(img, (xo, yo, xo+w, yo+h))
                    bg_white.paste(img, (xo, yo, xo+w, yo+h))
                    
                    # then save it
                    bg.save('%s/.thumb/%s' % (pathdir, filename), "PNG")
                    bg_white.save('%s/.thumb-whitebg/%s' % (pathdir, filename), "PNG")
                    
            
            except IOError:
                print "error sending file"

        return HttpResponse('%s' % filename)


@permission_required_with_403('upload.upload_write')
def attach_form(request, object_id = '', referral_id = ''):
    user = request.user
    referral = Referral.objects.get(pk = referral_id)
    organization = user.get_profile().org_active.id
    
    types = REFERRAL_ATTACH_TYPE

    #indication = Indication.objects.get(referral = object_id)
    attachs = ReferralAttach.objects.filter(referral = referral_id)
    object = Client.objects.get(pk = object_id)

    return render_to_response('upload/upload_attach.html', locals(), context_instance=RequestContext(request))

@permission_required_with_403('upload.upload_write')
def attach_save(request, object_id = None, client_id = None):

    if request.method == 'POST':
        user = request.user
        filename = ''

        if 'file' in request.FILES:
            path = '%simg/organization/%s' % (MEDIA_ROOT, user.get_profile().org_active.id)
            if not os.path.exists(path):
                os.mkdir(path)
                os.chmod(path, 0777)

            path = '%simg/organization/%s/attach' % (MEDIA_ROOT, user.get_profile().org_active.id)
            if not os.path.exists(path):
                os.mkdir(path)
                os.chmod(path, 0777)

            try:
                    filename = request.FILES['file']
                    file = str(uuid.uuid4()) + '.'+ (str(filename).split('.')[-1])
                    destination = open('%s/%s' % (path,  file), 'w+')
                    for chunk in filename.chunks():
                        destination.write(chunk)
                    destination.close()
                        
                    attachs = ReferralAttach.objects.filter(referral = object_id)               

                    attach = ReferralAttach()
                    attach.filename = '%s' % request.FILES['file']
                    attach.file = '%s' % file
                    attach.description = request.POST.get('description')
                    attach.type = request.POST.get('doc_type')
                    attach.referral = Referral.objects.get(pk = object_id)
                    attach.save()
    
            except IOError:
                print "error sending file"

        return HttpResponseRedirect('/upload/client/%s/attach/%s/' % (client_id, object_id))
