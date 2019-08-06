class CreateForm extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            blog_id : props.blog_id,
            title : "",
            digest : "",
            content : "",
            category: "blogs",
            method: "create",
            view: 0,
        }
        if(props.blog_id!=null){
            this.get_previous_blog(props.blog_id);
        }
    }

    get_previous_blog(blog_id){
        var xhr = new XMLHttpRequest();
        xhr.open('GET','/api/blogs/'+blog_id)
        xhr.onreadystatechange = ()=>{
            if(xhr.readyState === 4 && xhr.status === 200){
                const text = JSON.parse(xhr.responseText);
                this.setState({
                    title: text.title,
                    digest: text.digest,
                    category: text.category,
                    content: text.content,
                    method: "update"
                })
            }
        }
        xhr.send()
    }

    delete_current_blog(){
        if(confirm("Are you sure to delete the blog?")){
            var dumb = JSON.stringify({1:2})
            var xhr = new XMLHttpRequest();
            xhr.open('POST','/api/blogs/'+this.state.blog_id+'/delete')
            xhr.setRequestHeader('Content-Type','application/json')
            xhr.onreadystatechange = ()=>{
                if(xhr.readyState === 4 && xhr.status === 200){
                    const text = JSON.parse(xhr.responseText);
                    if('error' in text){
                        window.alert(text.error+'\n'+text.data+'\n'+text.message)
                    }else{
                        window.alert("Succeed");
                    }
                }
            }
            xhr.send(dumb)
        }
    }

    submit(event){
        event.preventDefault();
        event.stopPropagation();
        var url,data=JSON.stringify({
            title:this.state.title,
            digest:this.state.digest,
            content:this.state.content,
            category:this.state.category,
        });

        if(this.state.method=="create"){
            url = "/api/blogs";
        }else{
            url = "/api/blogs/"+this.state.blog_id;
        }
        if(event.target.checkValidity() != false){
            var xhr = new XMLHttpRequest();
            xhr.open('POST',url);
            xhr.setRequestHeader('Content-Type','application/json')
            xhr.onreadystatechange = ()=>{
                if(xhr.readyState === 4&&xhr.status === 200){
                    const text = JSON.parse(xhr.responseText);
                    if('error' in text){
                        window.alert(text.error+'\n'+text.data+'\n'+text.message);
                    }else{
                        window.alert("Succeed")
                    }
                }
            }
            xhr.send(data)
        }
        event.target.classList.add('was-validated');
    }

    render(){
        var textbox;
        var btn_name;
        var add_btn;
        if(this.state.method=='create')
        {
            btn_name = "create"
            add_btn = null;
        }else{
            btn_name = "update"
            add_btn = <button type="button" className="btn btn-primary mx-2 my-2" style={{float:'left'}}  onClick={()=>this.delete_current_blog()}>delete</button>
        }
        if(this.state.view==0){
            textbox = (
                <textarea id="post_content" value={this.state.content} style={{resize:'none',width:'100%',height:'700px'}} className="mb-2" onChange={(e)=>{this.setState({content:e.target.value})}}>
                </textarea>
            );
        }
        else{
            textbox = (
                <div id="post_content" style={{height:'700px',width:'100%',overflow:'auto',}} 
                dangerouslySetInnerHTML={{__html:convert(this.state.content)}}>

                </div>
            )
        }
        return (
            <div className="my-3">
                <form className="needs-validation" noValidate id="create_post_form" onSubmit={(e)=>{this.submit(e)}}>
                    <div className="form-group">
                        <h3 htmlFor="post_title">Title</h3>
                        <input type="text" value={this.state.title} id="post_title" className="form-control" placeholder="title of your post" onChange={(e)=>{this.setState({title:e.target.value})}} required></input>
                        <div className="valid-feedback">OK</div>
                        <div className="invalid-feedback">Please fill out this field.</div>
                    </div>
                    <div class="form-group">
                        <h3 htmlFor="post_category">Category</h3>
                        <select class="custom-select" value={this.state.category} onChange={(e)=>this.setState({category:e.target.value})} id="post_category">
                            <option value="blogs">blogs</option>
                            <option value="tutorials">tutorials</option>
                            <option value="leetcode">leetcode</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <h3 htmlFor="post_digest">Subtitle</h3>
                        <input type="text" value={this.state.digest} id="post_digest" className="form-control" placeholder="briefly introduce the content" onChange={(e)=>{this.setState({digest:e.target.value})}} required maxLength="400"></input>
                        <div className="valid-feedback">OK</div>
                        <div className="invalid-feedback">Please fill out this field.</div>
                    </div>
                    <div className="form-group">
                        <h3 htmlFor="post_content">Content</h3>
                        <ul className="nav nav-tabs">
                            <li className="nav-item">
                                <a className="nav-link" href="javascript:void(0);" onClick={()=>this.setState({view:0})}>Edit</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link" href="javascript:void(0);" onClick={()=>this.setState({view:1})}>Preview</a>
                            </li>
                        </ul>
                        {textbox}
                    </div>
                    <button type="submit" className="btn btn-primary my-2" style={{float:'left'}}>{btn_name}</button>
                    {add_btn}
                </form>
            </div>
        )

    }
}

var init = document.getElementById('blog_form').innerText
var init_blog = init === ""?null:init;
ReactDOM.render(<CreateForm blog_id={init_blog}/>,document.getElementById("blog_form"))