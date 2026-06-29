from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.accounts.forms import CustomUserCreationForm, UserUpdateForm

# View Đăng ký
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/auth_page.html', {
        'form': form, 
        'title': 'Đăng ký thành viên', 
        'action_name': 'Đăng ký', 
        'is_login': False
    })

# View Đăng nhập
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu. Vui lòng nhập lại chính xác.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/auth_page.html', {
        'form': form, 
        'title': 'Đăng nhập', 
        'action_name': 'Đăng nhập', 
        'is_login': True
    })

# View Đăng xuất
def logout_view(request):
    logout(request)
    return redirect('home')

# View Chỉnh sửa Hồ sơ cá nhân
@login_required
def profile_edit(request):
    if request.method == 'POST':
        # Dùng trực tiếp request.user để lưu ảnh và thông tin
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, "Cập nhật thông tin thành công!")
            return redirect('profile_edit')
    else:
        u_form = UserUpdateForm(instance=request.user)
        
    return render(request, 'accounts/profile_edit.html', {'u_form': u_form})