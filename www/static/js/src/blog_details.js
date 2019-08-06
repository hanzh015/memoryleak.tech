class Comment extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            /*
            id : props.id,
            user_name : props.user_name,
            user_image: props.image,
            content : props.content,
            created_at : props.created_at,
            */
           id : props.info.id,
           user_name : props.info.user_name,
           user_image : props.info.user_image,
           content : props.info.content,
           created_at : props.info.created_at,
        };
    }

    render() {
        const raw = convert(this.state.content);
        var datetime = function(time){
            var now = Date.now()/1000;
            if(now-time<60){
                return "a minute ago";
            }
            else if(now-time<3600){
                return "in an hour";
            }
            else if(now-time<86400){
                return "in a day";
            }
            else{
                var epoch = new Date(time*1000);
                return 'Posted on '+(epoch.getMonth()+1)+'/'+epoch.getDate()+'/'+epoch.getFullYear();
            }
        }
        return (
            <div>
                <div>
                    <img src={this.state.user_image} width="72" style={{float:'left'}}></img>
                    <span style={{float:'left'}}>
                        <div className="text-dark">{this.state.user_name}</div>
                        <div className="text-muted">{datetime(this.state.created_at)}</div>
                    </span>
                </div>
                <div className="p-1" dangerouslySetInnerHTML={{__html:raw}} style={{clear:'both'}}>
                </div>
                <hr/>
            </div>
        )
    };
}

class Comments extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            comments : props.comments,
            switch: props.switch,
        }
        //Directly assign to this.state. Don't call 
        //this.get_comments(props.page);
    }
    componentDidMount(){
        document.getElementById('CommentArea').querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
          });
    }

    render(){
        if(this.props.comments){

            const comments_list = this.props.comments.map((x,index)=>{
                return (
                    <Comment key={x.id} info={x}></Comment>
                );
            });
            //console.log(this.state.page);
            const button_list = Array(this.props.total).fill(0).map((ele,index)=>{
                return (<li key={1000+index*10} className="page-item">
                    <button className="page-link" onClick={()=>this.props.switch(index+1)}>{index+1}</button>
                </li>);
            });
            return (
                <div>
                    {comments_list}
                    <ul className="pagination justify-content-center">
                        <li className="page-item">
                            <button className="page-link" disabled={this.props.page==1} onClick={()=>{
                                if(this.props.page>1){
                                    this.props.switch(this.props.page-1);
                                }
                            }}> {"<<"} </button> 
                        </li>
                        {button_list}
                        <li className="page-item">
                            <button className="page-link" disabled={this.props.page==this.props.total} onClick={()=>{
                                if(this.props.page<this.props.total){
                                    this.props.switch(this.props.page-0+1);
                                }
                            }}> {">>"}</button>
                        </li>
                    </ul>
                </div>
            );
        }else{
            return <p>Be the first one to comment</p>
        }
    }
}

class Edit extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            post:props.post,
            view:0,
            onpostchange : props.onPostChange,
            onsubmit : props.onPost,
        }
    }
    toggle(state){
        if(this.state.view!=state){
            this.setState({
                view:state,
            })
        }
    }

    render(){
        var textbox;
        if(this.state.view==0){
            textbox = (
                <textarea value={this.props.post} style={{resize:'none',width:'100%',height:'200px'}} className="mb-3" onChange={(e)=>{this.state.onpostchange(e)}}>
                </textarea>
            );
        }
        else{
            textbox = (
                <div id="preview" style={{height:'200px',width:'100%',overflow:'auto',}} 
                dangerouslySetInnerHTML={{__html:convert(this.props.post)}}>

                </div>
            )
        }
        return (
            <div style={{overflow:'auto'}}>
                <ul className="nav nav-tabs">
                    <li className="nav-item">
                        <a className="nav-link" href="javascript:void(0);" onClick={()=>this.toggle(0)}>Edit</a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="javascript:void(0);" onClick={()=>this.toggle(1)}>Preview</a>
                    </li>
                </ul>
                {textbox}
                <button type="button" className="btn btn-outline-primary mx-1 my-1" style={{float:"right"}} onClick={this.state.onsubmit}>POST</button>
            </div>
        )
    }
    componentDidUpdate(){
        if(this.state.view==1){
            document.getElementById('preview').querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
              });
        }
    }
}

class CommentArea extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            blog_id : props.blog_id,
            post : "",
            comments_page : '1',
            comments : null,
            total : null,
        }
        this.get_comments(1);
    }

    submit(){
        if(this.state.post == ""){
            window.alert("The content should not be empty!")
        }else{
            var xhr = new XMLHttpRequest();
            xhr.open('POST','/api/comments',true);
            xhr.setRequestHeader('Content-Type','application/json')
            xhr.onreadystatechange = ()=>{
                if(xhr.readyState === 4 && xhr.status === 200){
                    const text = JSON.parse(xhr.responseText);
                    if('error' in text){
                        window.alert(text.error+'\n'+text.data+'\n'+text.message);
                    }else{
                        //when successfully upload new post, re-render comments to show page 1
                        this.get_comments(1);
                        this.setState({post:""});
                    }
                }
            }
            var data = JSON.stringify({
                blog_id: this.state.blog_id,
                content: this.state.post,
            });
            xhr.send(data);
        }
    }

    get_comments(p){
        //console.log(window.location.host)
        var url = "/api/comments?page=" + p + "&blog_id=" + this.state.blog_id;
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = ()=>{
            if(xhr.readyState === 4 && xhr.status===200){
                const text = JSON.parse(xhr.responseText);
                this.setState({
                    comments_page : p,
                    comments:text.comments,
                    total : text.total,
                });
            }
        };
        xhr.open('GET',url);
        xhr.send();
    }

    render(){
        return (
            <div>
                <Edit onPost={()=>{this.submit()}} post={this.state.post} onPostChange={(e)=>{this.setState({post:e.target.value});}}/>
                <h4>Comments</h4>
                <hr/>
                <Comments comments={this.state.comments} switch={(p)=>{this.get_comments(p)}} total={this.state.total} page={this.state.comments_page}/>
            </div>
        )
    }
}

const blog_id = document.getElementById('CommentArea').innerText;
ReactDOM.render(<CommentArea blog_id={blog_id}/>,document.getElementById('CommentArea'));
