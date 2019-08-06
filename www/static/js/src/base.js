class Dropdown extends React.Component{
    constructor(props){
        super(props)
        this.state = {
            user: props.user,
            register: false,
        }
    }
    
    submit(event){
        event.preventDefault();
        event.stopPropagation();
        if(event.target.id == 'login_form')
        {
            //log in
            if(event.target.checkValidity() === false){
            }else{
                var email = document.getElementById('log_in_email').value
                var passwd = document.getElementById('log_in_password').value
                //convert raw key to sha1 40 digit string
                var data = JSON.stringify({'email':email,
                'password':CryptoJS.SHA1(email+":"+passwd).toString()})
                var xhr = new XMLHttpRequest()
                xhr.open('POST','/api/login',true)
                xhr.setRequestHeader("Content-Type", "application/json");
                var exe = (text)=>{
                    if('error' in text){
                        window.alert(text.error+'\n'+text.data+'\n'+text.message)
                    }else{
                    this.setState({
                        user: text,
                    })
                }
                }
                xhr.onreadystatechange = ()=>{
                    if(xhr.readyState === 4 && xhr.status === 200){
                        const text = JSON.parse(xhr.responseText);
                        $.when($('#loginModal').modal('hide')).then(()=>exe(text))
                    }} 
                xhr.send(data)
            }
            event.target.classList.add('was-validated');
        }
        else
        {
            //register
            var checkMatch = function(){
                var psw = document.getElementById('register_password1').value;
                var psw2 = document.getElementById('register_password2').value;
                return psw === psw2;
            }
            if(event.target.checkValidity() === false || !checkMatch()){

            }else{
                var email = document.getElementById('register_email').value
                var passwd = document.getElementById('register_password1').value
                var name = document.getElementById('register_name').value
                var data = JSON.stringify({
                    'email': email,
                    'passwd':CryptoJS.SHA1(email+":"+passwd).toString(),
                    'name':name
                })
                var xhr = new XMLHttpRequest()
                xhr.open('POST','/api/users',true)
                xhr.setRequestHeader('Content-Type','application/json')
                xhr.onreadystatechange = ()=>{
                    if(xhr.readyState === 4 && xhr.status === 200){
                        const text = JSON.parse(xhr.responseText);
                        $('#loginModal').modal('hide')
                        if('error' in text){
                            window.alert(text.error+'\n'+text.data+'\n'+text.message)
                        }else{
                        this.setState({
                            user: text,
                        })
                    }
                    } 
                }
                xhr.send(data)
            }
            event.target.classList.add('was-validated');
        }
    }

    log_out(){
        //log out function
        var xhr = new XMLHttpRequest()
        xhr.open('POST','/api/logout',true)
        xhr.setRequestHeader('Content-Type','application/json')
        var dummy = JSON.stringify({})
        xhr.onreadystatechange = ()=>{
            if(xhr.readyState === 4 && xhr.status === 200){
                this.setState({
                    user: null,
                })
            }
        }
        xhr.send(dummy)

    }
    
    componentDidUpdate(){
        $('.dropdown-menu').removeAttr('style');
    }

    confirmPassword(){
        var psw1 = document.getElementById('register_password1');
        var psw2 = document.getElementById('register_password2');
        if(psw1.value != psw2.value){
            psw2.setCustomValidity("Passwords Don't Match");
        }else{
            psw2.setCustomValidity('');
        }
    }
    render(){
        var menu_items;
        if(this.state.user){
            //logged in successfully
            var manage;
            if(this.state.user.admin=='1'){
                manage = (
                    <div>
                        <div className="dropdown-divider"></div>
                        <a className="dropdown-item" href="/manage/users">Admin Stuff</a>
                    </div>
                )
            }else{
                manage = (<div></div>);
            }
            menu_items = (
                <div className="dropdown-menu dropdown-menu-right" aria-labelledby="logindrop" style={{display:'?'}}>
                    <a className="dropdown-item" href="#"><img src={this.state.user.image} width='72'></img></a>
                    <a className="dropdown-item" href="#">My Account</a>
                    <a className="dropdown-item" href="/manage/blogs">My post</a>
                    <a className="dropdown-item" href="/manage/comments">My comments</a>
                    <a className="dropdown-item" href="/manage/blogs/create">Post a new blog</a>
                    {manage}
                    <div className="dropdown-divider"></div>
                    <a className="dropdown-item" href="javascript:void(0);" onClick={()=>this.log_out()}>Log out</a>
                </div>
            )
            var name_display = this.state.user.name.length>12?(this.state.user.name.substr(0,9)+'...'):this.state.user.name;
            return (
                <div className="navbar-nav dropdown mx-sm-2" style={{width:'165px'}}>
                    <a className="navbar-item nav-link dropdown-toggle" href='#' 
                    id="logindrop" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" key="user-toggle">
                         <i className="fas fa-user fa-lg mx-1"></i>  {name_display}
                    </a>
                    {menu_items}
                </div> 
            )
        }else{
            var login_form = (
                <form className="needs-validation" noValidate id="login_form" onSubmit={(e)=>{this.submit(e)}}>
                    <div className="form-group">
                        <label htmlFor="log_in_email">Email:</label>
                        <input type="email" className="form-control" id="log_in_email" placeholder="Enter email" name="email" required/>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">Please fill out this field.</div>
                    </div>
                    <div className="form-group">
                        <label htmlFor="log_in_password">Password:</label>
                        <input type="password" className="form-control" id="log_in_password" placeholder="Enter password" name="password" required/>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">Please fill out this field.</div>
                    </div>
                    <div className="form-group form-check">
                        <label className="form-check-label">
                            <input className="form-check-input" type="checkbox" name="remember"/> Remember my login state for 7 days.
                        </label>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">Please fill out this field.</div>
                    </div>
                    <button type="submit" className="btn btn-primary">Submit</button>
                </form>
            )

            var register_form = (
                <form className="needs-validation" noValidate id="register_form" onSubmit={(e)=>{this.submit(e)}}>
                    <div className="form-group">
                        <label htmlFor="register_email">Email:</label>
                        <input type="email" className="form-control" id="register_email" placeholder="Enter email" name="email" required/>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">Your input should be valid email address.</div>
                    </div>
                    <div className="form-group">
                        <label htmlFor="register_name">NickName</label>
                        <input type="text" className="form-control" id="register_name" placeholder="Enter email" name="email" required/>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">Please fill out this field.</div>
                    </div>
                    <div className="form-group">
                        <label htmlFor="register_password1">Password:</label>
                        <input type="password" className="form-control" id="register_password1" placeholder="Enter password" name="password" required/>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">Please fill out this field.</div>
                    </div>
                    <div className="form-group">
                        <label htmlFor="register_password2">Confirm Password:</label>
                        <input type="password" className="form-control" id="register_password2" placeholder="Enter password" name="cpassword" onChange={()=>{this.confirmPassword()}} required/>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">The passwords don't match.</div>
                    </div>
                    <div className="form-group form-check">
                        <label className="form-check-label">
                            <input className="form-check-input" type="checkbox" name="remember" required/> I have known blabla.
                        </label>
                        <div className="valid-feedback">Valid.</div>
                        <div className="invalid-feedback">Please read and admit our policy.</div>
                    </div>
                    <button type="submit" className="btn btn-primary">Submit</button>
                </form>
            )

            var form_display = this.state.register?register_form:login_form;
            var l_active_state = this.state.register?" ":" active";
            var r_active_state = this.state.register?" active":" ";

            return (
                <div style={{width:'165px'}}>
                    <ul className="navbar-nav mr-auto">
                        <li className="nav-item mx-2" key="awesome-register">
                            <a type="button" className="nav-link" data-toggle="modal" data-target="#loginModal">
                            <i className="fas fa-sign-in-alt fa-lg mx-1"></i> Login/SignUp</a>
                        </li>
                    </ul>
                    <div className="modal" id="loginModal">
                        <div className="modal-dialog modal-dialog-centered">
                            <div className="modal-content">
                                <div className="modal-header">
                                    <h4 className="modal-title">Log in before you shine</h4>
                                    <button type="button" className="close" data-dismiss="modal">&times;</button>
                                </div>
                                <div className="modal-body">
                                    <ul className="nav nav-pills justify-content-center">
                                        <li className="nav-item">
                                            <a className={"nav-link"+l_active_state} href="javascript:void(0);" onClick={()=>this.setState({register:false})}>Log in</a>
                                        </li>
                                        <li className="nav-item">
                                            <a className={"nav-link"+r_active_state} href="javascript:void(0);" onClick={()=>this.setState({register:true})}>Register</a>
                                        </li>
                                    </ul>
                                    {form_display}
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-danger" data-dismiss="modal" id="close">Close</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }
    }
}

var user_info = document.getElementById('user').innerText;
user_info = JSON.parse(user_info)
user_info = user_info.status=='Succeed'?user_info:null;
ReactDOM.render(<Dropdown user={user_info}/>,document.getElementById('user'))