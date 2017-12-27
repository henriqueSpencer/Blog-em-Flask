from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
#o sqlalchema cria uma interface entre o banco e uma class python
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date

from wtforms.ext.sqlalchemy.fields import QuerySelectField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
Bootstrap(app)
db = SQLAlchemy(app) # obj de acesso ao banco
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique= True)
	email = db.Column(db.String(50), unique= True)
	password = db.Column(db.String(80))
	#so para qunado criar um novo usuario ja passar os seus valores
	#def __init__(self, username, email, password):
	#	self.username = username
	#	self.email= email
	#	self.password= password
#db.create_all()

class Texto(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	titulo = db.Column(db.String(15), unique= True)
	texto = db.Column(db.String(1000), unique= True)
	descricao = db.Column(db.String(200))
	coautores = db.Column(db.String(80))
	autor = db.Column(db.Integer)
	data = db.Column(db.String(80))
	
class Comentario(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	idpost =db.Column(db.Integer)
	comentario= db.Column(db.String(200))
#########################################################	
#db.create_all()

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max =15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max =80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'),Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max =15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max =80)])

class RegisterText(FlaskForm):
	titulo = StringField('titulo', validators=[InputRequired(),Length(max=15)])
	#texto = StringField('texto', validators=[InputRequired()], widget=TextArea())
	texto = StringField('texto', validators=[InputRequired(), Length(min=4, max =1000)])
	descricao = StringField('descricao', validators=[InputRequired(), Length(min=4, max =200)])
	#coautores = StringField('coautores', validators=[InputRequired(), Length(min=8, max =80)])
	#coautores = QuerySelectField('coautores', query_factory=lambda: User.query.all())
	#coautores = QuerySelectField('Select Users', query_factory=User.query.all, get_label=lambda u: u.username)
	coautores = QuerySelectField(u'coautores', query_factory=lambda: User.query.all(), get_label='username')

class RegisterComentario(FlaskForm):
	comentario = StringField('comentario', validators=[InputRequired(), Length(min=4, max =200)])


@app.route('/')
def index():
	texto = Texto.query.all()
	return render_template('index.html', texto=texto)


@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:		#compara o hash do banco com a transformacao da senha passa em hash
			if check_password_hash(user.password, form.password.data):
			#if user.password == form.password.data:
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))

		return '<h2> Invalid username or password </h1>'
		#return '<h1>' + form.username.data + ' ' +form.password.data + '</h1>' 


	return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method= 'sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		#new_user = User(username=form.username.data, email=form.username.data, password=form.password.data)
		db.session.add(new_user)
		db.session.commit()

		return '<h1> New user has been create, porra </h1>'
		#return '<h1>' + form.username.data + ' '+form.email.data + ' ' +form.password.data + '</h1>' 

	return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required #para nao poder acessar diretamente
def dashboard():
	idusuario = current_user.id
	texto = Texto.query.filter_by(autor=idusuario)
	return render_template('dashboard.html', name = current_user.username, texto=texto)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/fazertexto', methods=['GET','POST'])
@login_required
def fazertexto():
	form = RegisterText()
	aul = current_user.id
	if form.validate_on_submit():
		hj = date.today()
		new_Texto = Texto(titulo=form.titulo.data, texto=form.texto.data, descricao=form.descricao.data, coautores=form.coautores.data, autor=aul, data=hj)
		#new_user = User(username=form.username.data, email=form.username.data, password=form.password.data)
		db.session.add(new_Texto)
		db.session.commit()

		return '<h1> New texto has been create, porra </h1>'
		#return '<h1>' + form.username.data + ' '+form.email.data + ' ' +form.password.data + '</h1>' 


	return render_template('fazertexto.html', form=form)


@app.route('/textoCompleto/<int:id>', methods=['GET','POST'])
def abrirTexto(id):

	#texto = Texto.query.filter_by(id=id).first()
	textt = Texto.query.get(id)
	user = User.query.get(textt.autor)

	titulo=textt.titulo
	autores= "autor: " + user.username + ", coautores: " + textt.coautores 
	descricao= textt.descricao
	texto= textt.texto
	data = textt.data

	form = RegisterComentario()
	
	comentario = Comentario.query.filter_by(idpost=id)

	if form.validate_on_submit():
		new_Comentario = Comentario( idpost=id, comentario=form.comentario.data )
		#new_user = User(username=form.username.data, email=form.username.data, password=form.password.data)
		db.session.add(new_Comentario)
		db.session.commit()

		return '<h1> New comentario has been create, porra </h1>'
		#return '<h1>' + form.username.data + ' '+form.email.data + ' ' +form.password.data + '</h1>' 

	return render_template('textoCompleto.html', titulo=titulo, autores=autores, texto=texto, descricao=descricao, id=id, form=form, comentario=comentario, data=data)

#select * from pessoas;


#delete from aultores where idAutor = valor

#@app.route("/excluir/<int:id>")
#def excluir(id):
#	pessoa =Pessoa.query.filter_by(_id=id).first()
#	db.session.delete(pessoa)
#	db.session.commit()
#
#	
#	pessoas = Pessoa.query.all()
#	return render_template("lista.html" , pessoas=pessoas )
###########################################################
#@app.route('/comentario/<int:id>', methods=['GET','POST'])
#def comentario(id):
#	form = RegisterComentario()
#
#	if form.validate_on_submit():
#		new_Comentario = Comentario( id=id, comentario=form.comentario.data )
#		#new_user = User(username=form.username.data, email=form.username.data, password=form.password.data)
#		db.session.add(new_Comentario)
#		db.session.commit()
#
#		return '<h1> New comentario has been create, porra </h1>'
#		#return '<h1>' + form.username.data + ' '+form.email.data + ' ' +form.password.data + '</h1>' 
#
#
#	return render_template('comentario.html', form=form, id=id)


if __name__ == '__main__':
	app.run(debug=True)
















