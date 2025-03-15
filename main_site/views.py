from django.conf import settings
from django.db import utils
from django.views.generic import TemplateView
from django_tenants.utils import remove_www
from schools.models import Client, Domain
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django_tenants.utils import schema_context, schema_exists
from authentication.models import User
from sms.sms_sender import send_sms
from sms.models import *
from django.contrib import messages
from .forms import UpdateSchoolForm, SchoolDeleteForm, SchoolAddForm
from django.contrib.auth.hashers import check_password
from sms.decorators import site_su_required

@login_required(login_url='/login/')
@site_su_required
def dashboard(request):
    template = 'authenticated/dashboard.html'
    tenants = Client.objects.exclude(schema_name='public')
    students_count = 0
    for tenant in tenants:
        with schema_context(tenant.schema_name):
            students_count += User.objects.filter(is_student=True).count()
    target = 500 * students_count # N500 times Number of students in all tenants
    context = {"tenants_count": tenants.count()}
    context['students_count'] = students_count
    context['target'] = target
    return render(request, template, context)

@login_required(login_url='/login/')
@site_su_required
def schools_list(request):
    context = {}
    tenants_list = Client.objects.exclude(schema_name='public')
    context['tenants_list'] = tenants_list
    template = 'authenticated/schools_list.html'
    return render(request, template, context)

@login_required(login_url='/login/')
@site_su_required
def school_add(request):
    template = 'authenticated/schools_add.html'
    return render(request, template, {})

import re
def special_match(strg, search=re.compile(r'[^a-z0-9.]').search):
    return not bool(search(strg))

@login_required(login_url='/login/')
@site_su_required
def school_add_save(request):
    if request.is_ajax():
        if request.method == "POST":
            form = SchoolAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                #tenant related data
                school_name = data.get('school_name')
                subdomain = data.get('subdomain')
                description = data.get('description')
                on_trial = data.get('ontrial')
                active_until = data.get('active_until')

                # user related data
                admin_email = data.get('email')
                phone = data.get('phone')
                username = data.get('username')
                password = data.get('password')

                if not special_match(subdomain):
                    return HttpResponse(2) # special character is found

                if schema_exists(subdomain):
                    return HttpResponse(3) # client already exist
                else:
                    tenant = Client(schema_name=subdomain,
                            name=subdomain,
                            description=description,
                            on_trial=False,
                            active_until=active_until)
                    tenant.save() # migrate_schemas will automatically be called

                    # Create Domain
                    domain = Domain()
                    domain.domain = '{}.localhost:8000'.format(subdomain)
                    domain.tenant = tenant
                    domain.is_primary = True
                    domain.save()

                    with schema_context(tenant.schema_name):
                        admin = User.objects.create_superuser(
                            username=username,
                            password=password,
                            email=admin_email,
                            phone=phone
                        )
                        Setting.objects.create(
                            school_name=school_name, 
                            business_email=admin_email,
                            business_phone1=phone).save()
                        Notification.objects.create(
                            user=admin,
                            title='Welcome to Bitpoint inc.',
                            body='Hello {} and  Welcome to Bitpoint Inc., \
                                  we wish you and the entire a happy schooling. \
                                  Thank you for choosing bitpoint',
                            message_type='Info')
                        message = 'Dear {}, Welcome to Bitpoint inc.,\
                                    please login to http://{}/app\
                                    using username: {} and password: {}\
                                    '.format(school_name, domain.domain, username, password)
                        send_sms(phone=phone, msg=message)
                    tenant.school_admin=admin
                    tenant.save()
                    return HttpResponse('success')
            else:
                form = SchoolAddForm(request.POST)
                template = "authenticated/ajax/school_add_form_not_valid.html"
                context =  {
                    "form": form,
                }
                return render(request, template, context)
        else:
            return HttpResponse('Get')


@login_required(login_url='/login/')
@site_su_required
def school_change(request, tenant_id):
    if request.method == "GET":
        template = 'authenticated/school_change.html'
        tenant = get_object_or_404(Client, id=tenant_id)
        context = {"tenant": tenant}
        return render(request, template, context)

@login_required(login_url='/login/')
@site_su_required
def schools_view(request, tenant_id):
    context = {}
    template = 'authenticated/school_view.html'
    school = get_object_or_404(Client, id=tenant_id)
    context['school'] = school
    with schema_context(school.schema_name):
        no_students = User.objects.filter(is_student=True).count()
        no_teachers = User.objects.filter(is_teacher=True).count()
        no_parents = User.objects.filter(is_parent=True).count()
        setting = Setting.objects.first()

        context['no_students'] = no_students
        context['no_parents'] = no_parents
        context['no_teachers'] = no_teachers
        context['setting'] = setting
    return render(request, template, context)


@login_required(login_url='/login/')
@site_su_required
def schools_sms_sub_update(request):
    if request.is_ajax():
        tenant_id = request.GET.get('tenant_id')
        sms_unit = request.GET.get('sms_unit')
        tenant = Client.objects.get(id=tenant_id)
        print("sms_unit==================== "+sms_unit)
        with schema_context(tenant.schema_name):
            setting = Setting.objects.first()
            setting.sms_unit += int(sms_unit)
            setting.save()
            print('Updated--------------------------')
        return HttpResponse(setting.sms_unit)

@login_required(login_url='/login/')
@site_su_required
def schools_sms_sub(request):
    template = 'authenticated/schools_sms_sub.html'
    context = {}
    tenants = Client.objects.exclude(schema_name='public')
    context['tenants'] = tenants
    return render(request, template, context)


@login_required(login_url='/login/')
@site_su_required
def site_backup(request, tenant_id):
    # TODO, Not working yet
    from django.contrib.contenttypes.models import ContentType
    import csv
    tenant = get_object_or_404(Client, id=tenant_id)
    with schema_context(tenant.schema_name):
        # Backup individual table as excel
        content_types = ContentType.objects.filter(app_label='sms')
        for model in content_types:
            model_objects = model.model_class().objects.all() # eg User.objects.all()
            if model_objects:
                fields = []
                print('================================{}=================='.format(model.model))
                # get list of fields (columns) for each model (table)
                # eg for class table will data like below 
                # ['student', 'subjectassign', 'feetype', 'id', 'name', 'section', 'amount_to_pay', 'subjects']
                fields = [field.name for field in model_objects.first()._meta.get_fields()]
                values = [value for value in model_objects.all()]
                print(values)
                response = HttpResponse(model_objects , content_type='application/vnd.ms-excel;charset=utf-8')
                response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(model.model)

                writer = csv.writer(response, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(fields[3:])
                for data in model_objects:
                    writer.writerow(values)
        return response


@login_required(login_url='/login/')
@site_su_required 
def school_change_save(request, tenant_id):
    if request.method == "POST":
        form = UpdateSchoolForm(request.POST)
        if form.is_valid():
            #tenant related data
            school_name = form.cleaned_data.get('school_name')
            subdomain = form.cleaned_data.get('subdomain')
            description = form.cleaned_data.get('description')
            on_trial = form.cleaned_data.get('ontrial')
            active_until = form.cleaned_data.get('active_until')

            # user related data
            admin_email = form.cleaned_data.get('email')
            print(admin_email)
            username = form.cleaned_data.get('username')
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data.get('password')
            user_id = form.cleaned_data.get('user_id')

            if Client.objects.filter(id=tenant_id).exists():
                tenant = Client.objects.get(id=tenant_id)
                tenant.name = school_name
                tenant.description = description
                if on_trial is not None:
                    tenant.on_trial = True
                else:
                    tenant.on_trial = False
                tenant.active_until = active_until

                with schema_context(tenant.schema_name):
                    admin = User.objects.get(id=user_id)
                    if password is not None:
                        admin.password=password
                    admin.email=admin_email
                    admin.phone=phone
                    admin.save()
                    tenant.school_admin=admin
                    tenant.save()

                    # update Domain
                    domain = Domain.objects.get(tenant_id=tenant_id)
                    if subdomain is not None:
                        domain.domain = '{}.localhost:8000'.format(subdomain)
                    domain.tenant = tenant
                    domain.is_primary = True
                    domain.save()
                messages.success(request, 'Updated Successfully !')
                return redirect('school_change', tenant_id=tenant_id)
            else:
                raise Http404
        else:
            tenant = get_object_or_404(Client, id=tenant_id)
            form = UpdateSchoolForm(request.POST)
            template = "authenticated/school_change.html"
            message = form
            context =  {
                "form": form,
                "message": message,
                "tenant": tenant,
            }
            return render(request, template, context)
    else:
        print("get")
        return redirect('school_change', tenant_id=tenant_id)

@login_required(login_url='/login/')
@site_su_required
def school_del(request):
    if request.is_ajax():
        form = SchoolDeleteForm(request.GET)
        template = 'authenticated/ajax/update_schools_table.html'
        if form.is_valid():
            user = request.user
            password = form.cleaned_data.get('password')
            school_id = form.cleaned_data.get('school_id')
            print(school_id)
            check = check_password(password, request.user.password)
            if check:
                client = get_object_or_404(Client, id=school_id)
                client.delete()
                tenants = Client.objects.exclude(schema_name='public')
                context = {"tenants_list": tenants}
                return render(request, template, context)
            else:
                return HttpResponse('incorrect_password')

class MainSiteHomeView(TemplateView):
    template_name = "public/index_public.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hostname_without_port = remove_www(self.request.get_host().split(':')[0])

        try:
            Client.objects.get(schema_name='public')

        except utils.DatabaseError:
            context['need_sync'] = True
            context['shared_apps'] = settings.SHARED_APPS
            context['tenants_list'] = []
            return context
            
        except Client.DoesNotExist:
            context['no_public_tenant'] = True
            context['hostname'] = hostname_without_port

        if Client.objects.count() == 1:
            context['only_public_tenant'] = True

        context['tenants_list'] = Client.objects.all()
        return context