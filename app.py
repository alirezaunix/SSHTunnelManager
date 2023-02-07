from flask import Flask, render_template, request, Response, render_template_string, stream_with_context,redirect,abort, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from simplepam import authenticate
import os

app=Flask(__name__)


app.config.update(
    DEBUG = True,
    SECRET_KEY = 'K3y4S3cr3T'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)
users = [User(id) for id in range(1, 21)]

@login_manager.user_loader
def load_user(userid):
    return User(userid)




def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest)
    except:
        return redirect(fallback)
    return redirect(dest_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        auth=authenticate(username,password,service='login',encoding='utf-8')
        print(">>>> in login method")
        if auth:
            user=User(username)
            print(">>>> in login ok")
            login_user(user)
            return  redirect_dest(fallback=url_for('index'))
        else:
            return render_template('login.html', msg='Wrong Username or Password')    
    else:
        return render_template('login.html', title='login Page')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect_dest(fallback=url_for('login'))

@app.route("/")
@login_required
def index():
    return render_template('index.html')

@app.route("/adduser", methods=["GET", "POST"])
@login_required
def adduser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        os.system(f'useradd -c "SSHUsers"  -p $(openssl passwd -1 {password}) {username}')
        return  redirect_dest(fallback=url_for('index'))
    else:
        return render_template('adduser.html')


@app.route("/userlist")
@login_required
def userlist():
    userlst=os.system("cat /etc/passwd | grep SSHUser").splitline()
    print(userlst)
    return 'ok'



if __name__=='__main__':
    app.run(debug=True,threaded=True,port=8088, host="0.0.0.0")
