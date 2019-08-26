class AdminControll extends React.Component{
    constructor(props) {
        super(props)
        this.state = {
            blog_page:1,
            blog_total:null,
            blog_items:null,
            comment_page:1,
            comment_total:null,
            comment_items:null,
            user_page:1,
            user_total:null,
            user_items:null,
            view: 'blog',
            page_size:'25'
        }
        this.fetch_items('blog',1);
        this.fetch_items('comment',1);
        this.fetch_items('user',1);
    }

    fetch_items(category,p){
        var url;
        if(category=="blog"){
            url = '/api/blogs?size='+this.state.page_size+'&page=' + p;
        }else if(category=='comment'){
            url = '/api/comments?size='+this.state.page_size+'&page=' + p;
        }else{
            url = '/api/users?size='+this.state.page_size+'&page=' + p;
        }
        var xhr = new XMLHttpRequest();
        xhr.open('GET',url);
        xhr.onreadystatechange = ()=>{
            if(xhr.readyState === 4&& xhr.status === 200){
                const text = JSON.parse(xhr.responseText);
                if('error' in text){
                    window.alert(text.error+'\n'+text.data+'\n'+text.message);
                }else{
                    if(category=='blog'){
                        this.setState({
                            blog_page:p,
                            blog_total:text.total,
                            blog_items:text.blogs
                        })
                    }
                    else if(category=='comment'){
                        this.setState({
                            comment_page:p,
                            comment_total:text.total,
                            comment_items:text.comments
                        })
                    }
                    else{
                        this.setState({
                            user_page:p,
                            user_total:text.total,
                            user_items:text.users
                        })
                    }
                }
            }
        }
        xhr.send();
    }

    delete_items(category,id){
        if(confirm("Are you sure you want to delete the current record?")){
            var url;
            switch(category){
                case "blog": url = '/api/blogs/'+id+'/delete';break;
                case "comment": url = '/api/comments/'+id+'/delete';break;
                case "user": url = '/api/users/'+id+'/delete';break;
                default: break;
            }
            var dummy = JSON.stringify({'1':'2'})
            var xhr = new XMLHttpRequest();
            xhr.open('POST',url);
            xhr.setRequestHeader('Content-Type','application/json');
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
            xhr.send(dummy);
        }

    }

    datetime = function(time){
        var epoch = new Date(time*1000);
        return (epoch.getMonth()+1)+'/'+epoch.getDate()+'/'+epoch.getFullYear();
    }

    blog_map = (x,index)=>{
        var bt,ac;
        if(x.title.length>50){
            bt=x.title.substr(0,47)+'...';
        }else{bt=x.title;}
        ac = (
            <div>
                <a type='button' className="btn btn-success btn-sm mx-1"
                 href="javascript:void(0);" onClick={()=>this.delete_items('blog',x.id)}>Del</a>
            </div>
        )
        return (
            <tr key={x.id}>
                <td>{this.state.page_size*(this.state.blog_page-1)+index-0+1}</td>
                <td><a href={"/blogs/"+x.blog_id} data-toggle="tooltip" data-placement="bottom" title={x.digest}>{bt}</a></td>
                <td>{x.user_name}</td>
                <td>{x.category}</td>
                <td>{this.datetime(x.created_at)}</td>
                <td>{ac}</td>
            </tr>
        )
    }

    blog_thead = (
        <tr>
            <th>#</th>
            <th>title</th>
            <th>user</th>
            <th>category</th>
            <th>created</th>
            <th>action</th>
        </tr>
    )

    comment_map = (x,index)=>{
        var bt,ct,ac;
        if(x.title.length>50){
            bt=x.title.substr(0,47)+'...';
        }else{bt=x.title;}
        if(x.content.length>50){
            ct=x.content.substr(0,47)+'...';
        }else{ct=x.content;}
        ac = (
            <div>
                <a type='button' className="btn btn-success btn-sm mx-1" 
                href="javascript:void(0);" onClick={()=>this.delete_items('comment',x.id)}>Del</a>
            </div>
        )
        return (
            <tr key={x.id}>
                <td>{this.state.page_size*(this.state.comment_page-1)+index-0+1}</td>
                <td><a href={"/blogs/"+x.blog_id} data-toggle="tooltip" data-placement="bottom" title={x.title}>{bt}</a></td>
                <td>{ct}</td>
                <td>{x.user_name}</td>
                <td>{this.datetime(x.created_at)}</td>
                <td>{ac}</td>
            </tr>
        )

    }

    comment_thead = (
        <tr>
            <th>#</th>
            <th>blog</th>
            <th>content</th>
            <th>user</th>
            <th>created</th>
            <th>action</th>
        </tr>
    )

    user_map = (x,index)=>{
        var ad = x.admin=='1'?'yes':'no';
        var ac = (
            <div>
                <a type='button' className="btn btn-success btn-sm mx-1" 
                href="javascript:void(0);" onClick={()=>this.delete_items('user',x.id)}>Del</a>
            </div>
        )
        return (
            <tr key={x.id}>
                <td>{this.state.page_size*(this.state.user_page-1)+index-0+1}</td>
                <td>{x.email}</td>
                <td>{x.name}</td>
                <td>{this.datetime(x.created_at)}</td>
                <td>{ad}</td>
                <td>{ac}</td>
            </tr>
        )

    }

    user_thead = (
        <tr>
            <th>#</th>
            <th>email</th>
            <th>name</th>
            <th>created</th>
            <th>admin</th>
            <th>action</th>
        </tr>
    )

    render(){
        var table;
        //row_map, switch_page, type, schema, col_num, page, items, total
        if(this.state.view=='blog'){
            table = <TableList key='blog' row_map={this.blog_map} switch_page={(p)=>{this.fetch_items('blog',p)}}
            type='blog' schema={this.blog_thead} col_num='5' page={this.state.blog_page} 
            items={this.state.blog_items} total={this.state.blog_total}/>
        }else if(this.state.view=='comment'){
            table = <TableList key='comment' row_map={this.comment_map} switch_page={(p)=>{this.fetch_items('comment',p)}}
            type='comment' schema={this.comment_thead} col_num='6' page={this.state.comment_page} 
            items={this.state.comment_items} total={this.state.comment_total}/>
        }else{
            //table = <h2>I'm really there</h2>
            table = <TableList key='user' row_map={this.user_map} switch_page={(p)=>{this.fetch_items('user',p)}}
            type='user' schema={this.user_thead} col_num='6' page={this.state.user_page} 
            items={this.state.user_items} total={this.state.user_total}/>
        }
        return (
            <div>
                <h2 className="my-3">Administration Panel</h2>
                <ul className="nav nav-tabs">
                    <li className="nav-item">
                        <a className="nav-link" href="javascript:void(0);" onClick={()=>this.setState({view:'blog'})}>Blog</a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="javascript:void(0);" onClick={()=>this.setState({view:'comment'})}>Comment</a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="javascript:void(0);" onClick={()=>this.setState({view:'user'})}>User</a>
                    </li>
                </ul>
                {table}
            </div>
        )

    }
}

class TableList extends React.Component{

    constructor(props){
        super(props);
        //row_map, switch_page, type, schema, col_num, page, items, total
    }

    render(){
        var rows;
        if(this.props.items==null){
            rows = null;
        }else{rows = this.props.items.map(this.props.row_map);}
        var pagenation;
        pagenation = Array(this.props.total).fill(0).map((ele,index)=>{
            return (<li key={this.props.type+index*10} className="page-item">
                <button className="page-link" onClick={()=>this.props.switch_page(index+1)}>{index+1}</button>
            </li>);
        });
        var navs;
        if(pagenation.length!=0){
            navs = (
                <ul className="pagination justify-content-center">
                <li className="page-item">
                    <button className="page-link" disabled={this.props.page==1} onClick={()=>{
                        if(this.props.page>1){
                            this.props.switch_page(this.props.page-1);
                        }
                    }}> {"<<"} </button> 
                </li>
                {pagenation}
                <li className="page-item">
                    <button className="page-link" disabled={this.props.page==this.props.total} onClick={()=>{
                        if(this.props.page<this.props.total){
                            this.props.switch_page(this.props.page-0+1);
                        }
                    }}> {">>"}</button>
                </li>
            </ul>
            )
        }else{
            navs = (
                <p>You currently don't have a record here!</p>
            )
        }
        return(
        <div>
            <table className="table table-striped">
                <thead>
                    {this.props.schema}
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            {navs}
        </div>
        )
    }
}

ReactDOM.render(<AdminControll/>,document.getElementById('list'))