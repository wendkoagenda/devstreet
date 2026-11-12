# 🐍 Conventions Django

## 📁 Structure des Projets

### Organisation générale

- **Projet principal** : `project_name/` (snake_case)
- **Applications** : dans un dossier `apps/` ou à la racine
- **Fichiers de configuration** : `.env`, `requirements.txt`, `README.md`
- **Dossiers statiques** : `static/`, `media/`, `templates/`, `locale/`

### Structure d'une application

- **Nom d'application** : snake_case (ex: `user_management`, `product_catalog`)
- **Fichiers principaux** : `models.py`, `views.py`, `urls.py`, `forms.py`, `admin.py`
- **DRF** : `serializers.py`, `permissions.py`
- **Utilitaires** : `managers.py`, `signals.py`, `utils.py`, `constants.py`
- **Tests** : dossier `tests/` avec `test_models.py`, `test_views.py`, etc.

## 🏷️ Conventions de Nommage

### Noms de Projets et Apps

```python
# ✅ Bon
my_project
user_management
product_catalog
order_processing

# ❌ Éviter
MyProject
UserManagement
productCatalog
```

### Modèles (Models)

```python
# ✅ Bon - PascalCase, singulier
class User(models.Model):
    pass

class ProductCategory(models.Model):
    pass

class OrderItem(models.Model):
    pass

# ❌ Éviter
class users(models.Model):  # Minuscule
    pass

class product_category(models.Model):  # snake_case
    pass
```

### Champs de Modèles

```python
# ✅ Bon - snake_case
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_address = models.EmailField()
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ❌ Éviter
class User(models.Model):
    firstName = models.CharField(max_length=50)  # camelCase
    LastName = models.CharField(max_length=50)   # PascalCase
```

### Relations

```python
# ✅ Bon
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
```

### Méthodes de Modèles

```python
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.pk})

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['last_name', 'first_name']
```

## 🎯 Vues (Views)

### Vues Basées sur les Fonctions

```python
# ✅ Bon - snake_case
def user_list(request):
    pass

def user_detail(request, user_id):
    pass

def create_user(request):
    pass

def update_user(request, user_id):
    pass

def delete_user(request, user_id):
    pass
```

### Vues Basées sur les Classes

```python
# ✅ Bon - PascalCase
class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'

class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user-list')
```

## 📋 Formulaires (Forms)

```python
# ✅ Bon - PascalCase avec suffixe Form
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email_address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
```

## 🔗 URLs

```python
# ✅ Bon - kebab-case pour les URLs
urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('create/', UserCreateView.as_view(), name='user-create'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('profile/', user_profile, name='user-profile'),
    path('change-password/', change_password, name='change-password'),
]

# Noms d'URLs - snake_case ou kebab-case
name='user_list'     # ✅ Acceptable
name='user-list'     # ✅ Préféré
name='userList'      # ❌ Éviter
```

### Nommage des Fichiers

```
templates/
├── base.html
├── users/
│   ├── user_list.html
│   ├── user_detail.html
│   ├── user_form.html
│   └── user_confirm_delete.html
├── products/
│   ├── product_list.html
│   └── product_detail.html
└── partials/
    ├── _navbar.html
    ├── _footer.html
    └── _pagination.html
```

### Variables de Contexte

```python
# ✅ Bon - snake_case
context = {
    'user_list': users,
    'total_count': total,
    'current_page': page,
    'is_authenticated': request.user.is_authenticated,
}
```

## 🔧 Serializers (DRF)

```python
# ✅ Bon - PascalCase avec suffixe Serializer
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email_address', 'full_name']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name()

class UserCreateSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email_address', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True}
        }
```

## 🗄️ Migrations

### Nommage des Migrations

```python
# ✅ Bon - Généré automatiquement
0001_initial.py
0002_add_user_profile.py
0003_alter_user_email.py
0004_remove_user_old_field.py

# Pour les migrations personnalisées
0005_populate_user_data.py
0006_update_permissions.py
```

## ⚙️ Settings

```python
# ✅ Bon - UPPER_CASE pour les constantes
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'my_database',
    }
}

# Variables personnalisées
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
DEFAULT_FROM_EMAIL = 'noreply@example.com'
SESSION_COOKIE_AGE = 3600  # 1 hour
```

## 🧪 Tests

```python
# ✅ Bon - PascalCase avec suffixe Test
class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john@example.com'
        )

    def test_user_str_representation(self):
        self.assertEqual(str(self.user), 'John Doe')

    def test_user_full_name_property(self):
        self.assertEqual(self.user.full_name, 'John Doe')

class UserViewTest(TestCase):
    def test_user_list_view(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)
```

## 🔒 Permissions et Groupes

```python
# ✅ Bon - snake_case avec préfixes clairs
class User(models.Model):
    class Meta:
        permissions = [
            ('can_view_user_profile', 'Can view user profile'),
            ('can_edit_user_profile', 'Can edit user profile'),
            ('can_delete_user_account', 'Can delete user account'),
        ]

# Groupes
ADMIN_GROUP = 'administrators'
MODERATOR_GROUP = 'moderators'
USER_GROUP = 'regular_users'
```

## 📝 Documentation et Commentaires

```python
class User(models.Model):
    """
    Modèle représentant un utilisateur du système.

    Attributes:
        first_name (str): Prénom de l'utilisateur
        last_name (str): Nom de famille de l'utilisateur
        email_address (str): Adresse email unique
        is_active (bool): Statut actif de l'utilisateur
    """

    first_name = models.CharField(
        max_length=50,
        verbose_name="Prénom",
        help_text="Prénom de l'utilisateur"
    )

    def get_full_name(self):
        """
        Retourne le nom complet de l'utilisateur.

        Returns:
            str: Prénom et nom séparés par un espace
        """
        return f"{self.first_name} {self.last_name}"
```

## 🚀 Bonnes Pratiques

1. **Utilisez des noms descriptifs** et évitez les abréviations
2. **Respectez la PEP 8** pour le style de code Python
3. **Utilisez des docstrings** pour documenter vos classes et méthodes
4. **Organisez vos imports** : stdlib, third-party, local
5. **Utilisez des constantes** pour les valeurs magiques
6. **Validez vos données** au niveau du modèle et du formulaire
7. **Utilisez les migrations** pour tous les changements de schéma
8. **Écrivez des tests** pour vos modèles, vues et formulaires
9. **Utilisez les signaux Django** avec parcimonie
10. **Séparez la logique métier** des vues dans des services ou managers
