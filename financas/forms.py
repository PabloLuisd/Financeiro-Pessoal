from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Transacao, Categoria, MetaFinanceira

class CadastroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, label='Senha')
    confirmar_senha = forms.CharField(widget=forms.PasswordInput, label='Confirmar senha')
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {'username': 'Nome de usuário', 'email': 'E-mail'}
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Já existe uma conta cadastrada com este e-mail.')
        return email
    def clean(self):
        data = super().clean()
        senha = data.get('senha')
        confirmar = data.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        if senha:
            try:
                validate_password(senha)
            except ValidationError as exc:
                self.add_error('senha', exc)
        return data
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email'].lower()
        usuario.set_password(self.cleaned_data['senha'])
        if commit:
            usuario.save()
        return usuario

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['tipo', 'descricao', 'valor', 'categoria', 'data', 'parcelas', 'parcela_atual', 'observacao']
        widgets = {'data': forms.DateInput(attrs={'type': 'date'}), 'observacao': forms.Textarea(attrs={'rows': 3})}
        labels = {'tipo': 'Tipo', 'descricao': 'Descrição', 'valor': 'Valor (R$)', 'categoria': 'Categoria', 'data': 'Data', 'parcelas': 'Número de parcelas', 'parcela_atual': 'Parcela atual', 'observacao': 'Observações'}
    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)
    def clean(self):
        data = super().clean()
        categoria = data.get('categoria')
        tipo = data.get('tipo')
        if categoria and tipo and categoria.tipo != tipo:
            self.add_error('categoria', 'Escolha uma categoria compatível com o tipo da transação.')
        return data

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'tipo', 'cor']
        widgets = {'cor': forms.TextInput(attrs={'type': 'color'})}
        labels = {'nome': 'Nome', 'tipo': 'Tipo', 'cor': 'Cor'}

class MetaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = MetaFinanceira
        fields = ['titulo', 'descricao', 'valor_objetivo', 'valor_atual', 'prazo']
        widgets = {'prazo': forms.DateInput(attrs={'type': 'date'}), 'descricao': forms.Textarea(attrs={'rows': 3})}
        labels = {'titulo': 'Nome da meta', 'descricao': 'Descrição', 'valor_objetivo': 'Valor objetivo (R$)', 'valor_atual': 'Valor já guardado (R$)', 'prazo': 'Prazo'}
