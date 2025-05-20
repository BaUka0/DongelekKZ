from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTPCode, SellerApplication
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active',]
    list_filter = ['role', 'is_staff', 'is_active',]
    search_fields = ['username', 'email',]
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'avatar', 'bio',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'avatar', 'bio',)}),
    )
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

class SellerApplicationAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'status', 'created_at', 'reviewed_at', 'application_actions']
    list_filter = ['status', 'created_at', 'reviewed_at']
    search_fields = ['user__username', 'user__email', 'reason', 'admin_comment']
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'reason', 'status')
        }),
        ('Қарау деректері', {
            'fields': ('admin_comment', 'reviewed_at')
        }),
    )
    
    def username(self, obj):
        return obj.user.username
    
    def email(self, obj):
        return obj.user.email
    
    def application_actions(self, obj):
        if obj.status == 'pending':
            approve_url = reverse('admin:approve_application', args=[obj.pk])
            reject_url = reverse('admin:reject_application', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}">Бекіту</a> '
                '<a class="button" style="background-color:#ba2121; color:white;" href="{}">Қабылдамау</a>',
                approve_url, reject_url
            )
        return '-'
    
    application_actions.short_description = 'Әрекеттер'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/', self.admin_site.admin_view(self.approve_application), name='approve_application'),
            path('<path:object_id>/reject/', self.admin_site.admin_view(self.reject_application), name='reject_application'),
        ]
        return custom_urls + urls
    
    def approve_application(self, request, object_id):
        application = self.get_object(request, object_id)
        if application:
            application.approve()
            self.message_user(request, f"Пайдаланушы {application.user.username} сатушы мәртебесі бекітілді", messages.SUCCESS)
            
            # Send email notification to user
            try:
                send_mail(
                    'Сатушы өтінішіңіз бекітілді',
                    f'Құрметті {application.user.username}, сіздің сатушы болу өтінішіңіз бекітілді. Енді сіз автокөліктерге жарнама жариялай аласыз.',
                    'noreply@dongelek.kz',
                    [application.user.email],
                    fail_silently=True,
                )
            except:
                pass
        
        return redirect('admin:accounts_sellerapplication_changelist')
    
    def reject_application(self, request, object_id):
        application = self.get_object(request, object_id)
        if application:
            application.reject()
            self.message_user(request, f"Пайдаланушы {application.user.username} сатушы өтініші қабылданбады", messages.WARNING)
            
            # Send email notification to user
            try:
                send_mail(
                    'Сатушы өтінішіңіз қабылданбады',
                    f'Құрметті {application.user.username}, өкінішке орай, сіздің сатушы болу өтінішіңіз қабылданбады. Қосымша ақпарат үшін әкімшілікпен байланысуыңызды сұраймыз.',
                    'noreply@dongelek.kz',
                    [application.user.email],
                    fail_silently=True,
                )
            except:
                pass
        
        return redirect('admin:accounts_sellerapplication_changelist')

admin.site.register(SellerApplication, SellerApplicationAdmin)