

import secrets

from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt

from hashlib import scrypt
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, current_app, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from functools import wraps
from flask_migrate import Migrate

from io import BytesIO

from openpyxl import Workbook




app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'defina'

# Configuração do banco de dados para usuários e registros de estoque
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Verificação de autenticação essa parte e responsavel por verificar se o usuario esta logado 
def verificar_autenticacao(rota):
    @wraps(rota)
    def decorador(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('homepage'))
        return rota(*args, **kwargs)
    return decorador


# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.office365.com'  # Servidor SMTP do Office 365
app.config['MAIL_PORT'] = 587  # Porta SMTP do Office 365
app.config['MAIL_USE_TLS'] = True  # Método de criptografia STARTTLS
app.config['MAIL_USERNAME'] = 'pablohenriquecoelhovinagre@outlook.com'  # Seu endereço de e-mail do Office 365
app.config['MAIL_PASSWORD'] = 'pablohenrique90'  # Sua senha de e-mail

mail = Mail(app)
# Adicionar logs ao enviar e-mails
try:
    # Código para enviar e-mail aqui
    app.logger.info('E-mail de redefinição de senha enviado com sucesso.')
except Exception as e:
    app.logger.error('Erro ao enviar e-mail de redefinição de senha: %s' % str(e))
    

@app.route("/logout")
def logout():
    # Verifica se o usuário está logado
    if 'username' in session:
        # Remove os dados da sessão associados ao usuário logado
        session.pop('username', None)
        session.pop('is_admin', None)

    # Redireciona para a página de login após o logout
    return redirect(url_for('homepage'))


# Definição da classe controle_de_estoque onde ficara armazenado os dados de item da informatica no banco de dados
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tecnico_responsavel = db.Column(db.String(80), nullable=False)
    item_type = db.Column(db.String(100), nullable=False)
    item_quantity = db.Column(db.Integer, nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    marca_text = db.Column(db.String(100), nullable=False)
    modelo_text = db.Column(db.String(100), nullable=False)
    lote_text = db.Column(db.String(100), nullable=False)
    data_abriu = db.Column(db.String(10), nullable=False)
    data_fechou= db.Column(db.String(10), nullable=False)

# Definição da classe de usuários no banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True) # Adicione esta linha
    is_admin = db.Column(db.Boolean, default=False)  # Campo para indicar se o usuário é um administrador
    reset_password_token = db.Column(db.String(100), unique=True)
    reset_password_expiration = db.Column(db.DateTime)
# Definição da classe para registros de estoque no banco de dados
class RegistroEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_entrada = db.Column(db.String(10), nullable=False)
    tombo = db.Column(db.String(20), nullable=False)
    serie = db.Column(db.String(20), nullable=False)
    setor = db.Column(db.String(20), nullable=False)
    tecnico_responsavel = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    peca_utilizada1 = db.Column(db.String(100))
    quantidade1 = db.Column(db.String(20))
    peca_utilizada2 = db.Column(db.String(100))
    quantidade2 = db.Column(db.String(20))
    peca_utilizada3 = db.Column(db.String(100))
    quantidade3 = db.Column(db.String(20))
    peca_utilizada4 = db.Column(db.String(100))
    quantidade4 = db.Column(db.String(20))
    data_saida = db.Column(db.String(10))
    status = db.Column(db.String(20),nullable=False)  # Novo campo para armazenar o status do item no estoque
    data_modificacao = db.Column(db.DateTime)
    usuario_modificacao = db.Column(db.String(80))
    modificacoes = db.relationship('RegistroModificacao', back_populates='registro')
class RegistroModificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_modificacao = db.Column(db.DateTime)
    usuario_modificacao = db.Column(db.String(80))
    registro_id = db.Column(db.Integer, db.ForeignKey('registro_estoque.id'))
    registro = db.relationship('RegistroEstoque', back_populates='modificacoes')
    
class inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tombo = db.Column(db.String(100))
    serie = db.Column(db.String(100))
    equipamento = db.Column(db.String(100))
    setor = db.Column(db.String(100))
    data = db.Column(db.String(10), nullable=False)
    
class registromouseteclado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tecnico_responsavel = db.Column(db.String(80), nullable=False)
    item_type = db.Column(db.String(100), nullable=False)
    item_quantity = db.Column(db.Integer, nullable=False)    
    item_requerente = db.Column(db.String(100), nullable=False)    
    lote_text = db.Column(db.String(100), nullable=False)
    data_abriu = db.Column(db.String(10), nullable=False)
    data_fechou= db.Column(db.String(10))


# Criação das tabelas no banco de dados (somente se ainda não existirem)
with app.app_context():
    db.create_all()



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^DESSE CAMPO PARA CIMA ESTA A PARTE DO BANCO DE DADOS E A CLASSE APP RESPONSAVEL PELA JANELA DO FLASK^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^





# Rota para exibir a página de estoque e lidar com adição de registros
@app.route('/estoque', methods=['GET', 'POST'])
@verificar_autenticacao
def estoque_page():
    if request.method == 'POST':
        # Obter os dados do formulário
        data_entrada = request.form['data_entrada']
        tombo = request.form['tombo']
        serie = request.form['serie']
        setor = request.form['setor']
        descricao = request.form['descricao']
        peca_utilizada1 = request.form['peca_utilizada1']
        quantidade1 = request.form['quantidade1']
        peca_utilizada2 = request.form['peca_utilizada2']
        quantidade2 = request.form['quantidade2']
        peca_utilizada3 = request.form['peca_utilizada3']
        quantidade3 = request.form['quantidade3']
        peca_utilizada4 = request.form['peca_utilizada4']
        quantidade4 = request.form['quantidade4']
        data_saida = request.form['data_saida']
        status = request.form['status']  # Obter o valor do campo 'status' do formulário

        # Validação do formulário (pode ser personalizada conforme a necessidade)
        if not data_entrada or not tombo or not serie or not descricao:
            return "Todos os campos são obrigatórios. Por favor, preencha novamente o formulário."

        # Obtém o nome de usuário do usuário logado a partir da variável de sessão 'session'
        tecnico_responsavel = session.get('username')

        # Criar novo registro de estoque no banco de dados
        novo_registro = RegistroEstoque(
            data_entrada=data_entrada,
            tombo=tombo,
            serie=serie,
            setor=setor,
            tecnico_responsavel=tecnico_responsavel,
            descricao=descricao,
            peca_utilizada1=peca_utilizada1,
            quantidade1=quantidade1,
            peca_utilizada2=peca_utilizada2,
            quantidade2=quantidade2,
            peca_utilizada3=peca_utilizada3,
            quantidade3=quantidade3,
            peca_utilizada4=peca_utilizada4,
            quantidade4=quantidade4,
            data_saida=data_saida,
            status=status  # Adiciona o campo 'status' ao novo registro
        )
        db.session.add(novo_registro)
        db.session.commit()

        # Redirecionar para a mesma página após a adição do registro
       

    # Recuperar todos os registros do estoque do banco de dados
    estoque = RegistroEstoque.query.all()
    
    # Renderizar o template e passar a lista de estoque para exibição na tabela
    return render_template('estoque.html', estoque=estoque)







# Campo responsavel pelo backend do EDITAR Registro realizado pelo tecnico
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@verificar_autenticacao
def editar_registro(id):
    registro = RegistroEstoque.query.get(id)
    tecnico_responsavel = session.get('username')
    if registro is None:
        return "Registro não encontrado."

    if request.method == 'POST':
        # Obter os dados do formulário de edição
        data_entrada = request.form['data_entrada']
        tombo = request.form['tombo']
        serie = request.form['serie']
        setor = request.form['setor']  # Adicionei o campo "setor"
        descricao = request.form['descricao']
        peca_utilizada1 = request.form['peca_utilizada1']
        quantidade1 = request.form['quantidade1']
        peca_utilizada2 = request.form['peca_utilizada2']
        quantidade2 = request.form['quantidade2']
        peca_utilizada3 = request.form['peca_utilizada3']
        quantidade3 = request.form['quantidade3']
        peca_utilizada4 = request.form['peca_utilizada4']
        quantidade4 = request.form['quantidade4']
        status = request.form['status']
        data_saida = request.form['data_saida']

        # Atualizar os campos do registro com os novos valores
        registro.data_entrada = data_entrada
        registro.tombo = tombo
        registro.serie = serie
        registro.setor = setor  # Atualiza o campo "setor"
        registro.descricao = descricao
        registro.peca_utilizada1 = peca_utilizada1
        registro.quantidade1 = quantidade1
        registro.peca_utilizada2 = peca_utilizada2
        registro.quantidade2 = quantidade2
        registro.peca_utilizada3 = peca_utilizada3
        registro.quantidade3 = quantidade3
        registro.peca_utilizada4 = peca_utilizada4
        registro.quantidade4 = quantidade4
        registro.status = status
        registro.data_saida = data_saida

        # Registrar o usuário e a data/hora da modificação
        usuario_modificacao = session.get('username')
        data_modificacao = datetime.now()
        registro.usuario_modificacao = usuario_modificacao
        registro.data_modificacao = data_modificacao

        # Criar um novo registro no log de modificação
        log_modificacao = RegistroModificacao(
            data_modificacao=data_modificacao,
            usuario_modificacao=usuario_modificacao,
            registro=registro
        )
        db.session.add(log_modificacao)

        db.session.commit()

        return redirect('/painel_inicial')

    return render_template('editar_registro.html', registro=registro)




@app.route('/excluir/<int:id>')
def excluir_registro(id):
    # Verifica se o usuário está logado e se é um administrador
    if 'username' in session and 'is_admin' in session and session['is_admin']:
        registro = RegistroEstoque.query.get(id)

        if registro:
            # Se o registro existe, exclui do banco de dados
            db.session.delete(registro)
            db.session.commit()

        # Redirecionar para a página de estoque após a exclusão
        return redirect('/estoque')
    else:
        return "Acesso não autorizado. Somente administradores podem excluir registros."






@app.route("/")
def homepage():
    return render_template("homepage.html")




@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        session['username'] = user.username
        session['is_admin'] = user.is_admin  # Armazena a informação se o usuário é administrador na sessão
        return redirect(url_for('painel_inicial'))

    return "Usuário ou senha inválidos."

#Verificação de autenticação essa parte e responsavel por verificar se o usuario esta logado 
def verificar_autenticacao(rota):
    @wraps(rota)
    def decorador(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return rota(*args, **kwargs)
    return decorador

@app.route('/solicitar_redefinicao_senha', methods=['GET', 'POST'])
def solicitar_redefinicao_senha():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')

        # Encontre o usuário pelo nome de usuário ou endereço de e-mail
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user:
            # Gere um token exclusivo e defina um prazo de validade
            token = secrets.token_urlsafe(32)
            expiration = datetime.utcnow() + timedelta(hours=1)  # Defina o prazo de validade para 1 hora

            # Armazene o token e o prazo de validade no banco de dados
            user.reset_password_token = token
            user.reset_password_expiration = expiration
            db.session.commit()

            # Envie um e-mail ao usuário com o link de redefinição de senha
            enviar_email_redefinicao_senha(user.email, token)

            return "Um e-mail com instruções para redefinir a senha foi enviado para o seu endereço de e-mail."

    return render_template('solicitar_redefinicao_senha.html')

# Função para enviar e-mail de redefinição de senha
def enviar_email_redefinicao_senha(destinatario_email, token):
    msg = Message('Redefinição de Senha', sender='pablohenriquecoelhovinagre@outlook.com', recipients=[destinatario_email])
    msg.body = f'Para redefinir sua senha, clique no seguinte link: {url_for("redefinir_senha", token=token, _external=True)}'
    mail.send(msg)

# Rota para redefinir a senha com base no token
@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    # Verificar se o token é válido (verifique se está dentro do prazo de validade)
    user = User.query.filter_by(reset_password_token=token).first()

    if user and user.reset_password_expiration > datetime.utcnow():
        if request.method == 'POST':
            # Obter a nova senha do formulário
            nova_senha = request.form.get('nova_senha')

            # Atualizar a senha do usuário no banco de dados
            user.password = nova_senha

            # Limpar o token e o prazo de validade
            user.reset_password_token = None
            user.reset_password_expiration = None

            db.session.commit()

            return "Senha redefinida com sucesso. Você pode fazer login com a nova senha."
        
        return render_template('redefinir_senha.html', token=token)
    
    return "Link de redefinição de senha inválido ou expirado."



@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        new_username = request.form.get("new_username")
        new_password = request.form.get("new_password")
        new_email = request.form.get("new_email")

        if User.query.filter_by(username=new_username).first():
            return "Nome de usuário já existe. Escolha outro."
        

        new_user = User(username=new_username, password=new_password, email=new_email,)
        db.session.add(new_user)
        db.session.commit()

        return "Senha redefinida com sucesso. Você pode fazer login com a nova senha.", redirect(url_for("user_info", username=new_username, login=new_username, email=new_email,))

    return render_template("cadastro.html")

# Dados simulados do usuário master (você pode substituir isso com um banco de dados real)
master_user = "admin"
master_password = "pablovugostoso2023"
is_master_admin = True




#painel onde podera verificar usuarios cadas
@app.route('/painel_usuario', methods=["GET", "POST"])
@verificar_autenticacao
def painelusuario():
    users = User.query.all()
    return render_template('painel_usuario.html', users=users)

#painel onde podera verificar usuarios cadas
@app.route('/painelmouseteclado', methods=["GET", "POST"])
@verificar_autenticacao
def painelmouseteclado():
    users = registromouseteclado.query.all()
    return render_template('painelmouseteclado.html', users=users)


# Rota para conceder privilégios de administrador
@app.route('/conceder_admin', methods=['GET', 'POST'])

def conceder_admin():
    
    if request.method == 'GET':
        return render_template('conceder_admin.html')

    if request.method == 'POST':
        master_username = request.form['master_username']
        master_password_input = request.form['master_password']
        new_admin_username = request.form['new_admin_username']

        if master_username == master_user and master_password_input == master_password and is_master_admin:
            # Verifica se o usuário que será concedido o privilégio de administrador existe no banco de dados
            new_admin_user = User.query.filter_by(username=new_admin_username).first()
            if new_admin_user:
                new_admin_user.is_admin = True  # Define o campo 'is_admin' como True para torná-lo um administrador
                db.session.commit()
                return "Privilégios de administrador concedidos com sucesso para o usuário: " + new_admin_username
            else:
                return "Usuário não encontrado."
        else:
            return "Falha ao conceder privilégios de administrador. Verifique as credenciais do usuário master."







@app.route("/painel_inicial") #Função que da acessoa pagina inicial
@verificar_autenticacao
def painel_inicial():
    tecnico_responsavel = session.get('username')
    return render_template("painel_inicial.html")










@app.route('/controle_de_estoque', methods=['GET', 'POST'])
@verificar_autenticacao
def controle_de_estoque():
    if request.method == 'POST':
        # Obtém o nome de usuário do usuário logado a partir da variável de sessão 'session'
        tecnico_responsavel = session.get('username')
        item_type = request.form.get('item_type')
        item_quantity = int(request.form.get('item_quantity'))
        serial_number = request.form.get('serial_number')
        marca_text = request.form.get('marca_text')
        modelo_text = request.form.get('modelo_text')
        lote_text = request.form.get('lote_text')
        data_abriu = request.form.get('data_abriu') 
        data_fechou = request.form.get('data_fechou') 
        
        new_item = Item(tecnico_responsavel= tecnico_responsavel, item_type=item_type, item_quantity=item_quantity, serial_number=serial_number, marca_text=marca_text, modelo_text=modelo_text, lote_text=lote_text, data_abriu= data_abriu, data_fechou= data_fechou)
        db.session.add(new_item)
        db.session.commit()
    
    items = Item.query.all()
    
    return render_template('controle_de_estoque.html', items=items)





@app.route('/estoque_panel')
@verificar_autenticacao
def estoque_panel():
    # Recupere os dados do banco de dados (substitua isso com sua lógica de consulta)
    estoque = RegistroEstoque.query.all()

    # Renderize o template HTML e passe os dados para ele
    return render_template('estoque_panel.html', estoque=estoque)

@app.route("/painel_inventario", methods=['GET','POST'])
@verificar_autenticacao
def controle_inventario():
    if request.method == 'POST':
        # Obtém o nome de usuário do usuário logado a partir da variável de sessão 'session'
        tombo = request.form.get('tombo')
        serie = request.form.get('serie')
        equipamento = request.form.get('equipamento')
        setor = request.form.get('setor')
        data = request.form.get('data')
        
        # Correção: Use um nome diferente para a variável do modelo
        inventario_lista = inventario(tombo=tombo, serie=serie, equipamento=equipamento, setor=setor, data=data)
        db.session.add(inventario_lista)
        db.session.commit()
    
    # Correção: Use um nome diferente para a variável de consulta
    inventario_lista = inventario.query.all()
    
    return render_template('painel_inventario.html', inventario_lista=inventario_lista)

@app.route("/camera.html", methods=["POST"])
@verificar_autenticacao
def abrir_camera():
    return render_template("camera.html")


@app.route('/grafico')
@verificar_autenticacao
def grafico():
    # Seu código para renderizar a página do gráfico aqui
    return render_template('grafico.html')
@app.route("/registromouseteclado", methods=['GET', 'POST'])
@verificar_autenticacao
def itemregistromouseteclado():
    if request.method == 'POST':
        # Obtém o nome de usuário do usuário logado a partir da variável de sessão 'session'
        tecnico_responsavel = request.form['tecnico_responsavel']
        item_type = request.form['item_type']
        item_quantity = request.form['item_quantity']
        item_requerente = request.form['item_requerente']
        lote_text = request.form['lote_text']
        data_abriu = request.form['data_abriu']
        data_fechou = request.form['data_fechou']
        
        if not item_type or not item_quantity or not item_requerente or not lote_text or not data_abriu:
            return "Todos os campos são obrigatórios. Por favor, preencha novamente o formulário."
   
        # Cria um novo objeto registromouseteclado com os dados fornecidos
        item = registromouseteclado(tecnico_responsavel=tecnico_responsavel,
                                    item_type=item_type,
                                    item_quantity=item_quantity,
                                    item_requerente=item_requerente,
                                    lote_text=lote_text,
                                    data_abriu=data_abriu,
                                    data_fechou=data_fechou)

        # Adiciona o novo objeto ao banco de dados
        db.session.add(item)
        db.session.commit()

    # Recupera todos os objetos registromouseteclado do banco de dados
    itens = registromouseteclado.query.all()

    return render_template('registromouseteclado.html', itens=itens)

if __name__ == "__main__":
    app.debug = True  # Ative o modo de depuração
    app.run(host="localhost")