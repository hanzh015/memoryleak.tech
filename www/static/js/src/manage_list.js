class ManageList extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            category: props.category,
            page: 1,
            page_total: null,
            numofitems: 25,
            items: null,
        }
        this.fetch_items(1);
    }

    fetch_items(p){
        var url;
        if(this.state.category=="blog"){
            url = '/api/blogs?user=True&size='+this.state.numofitems+'&page=' + p;
        }else if(this.state.category=='comment'){
            url = '/api/comments?user=True&size='+this.state.numofitems+'&page=' + p;
        }else{
            url = '/api/user?size='+this.state.numofitems+'&page=' + p;
        }
        var xhr = new XMLHttpRequest();
        xhr.open('GET',url);
        xhr.onreadystatechange = ()=>{
            if(xhr.readyState === 4&& xhr.status === 200){
                const text = JSON.parse(xhr.responseText);
                if('error' in text){
                    window.alert(text.error+'\n'+text.data+'\n'+text.message);
                }else{
                    var it;
                    if(this.state.category=='blog'){it=text.blogs;}
                    else if(this.state.category=='comment'){it=text.comments;}
                    else{it=text.users;}
                    this.setState({
                        items:it,
                        page_total:text.total,
                        page: p
                    })
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
    //how this website was built
    render(){
        var rows,head,table_title;
        var datetime = function(time){
            var epoch = new Date(time*1000);
            return (epoch.getMonth()+1)+'/'+epoch.getDate()+'/'+epoch.getFullYear();
        }
        const pagenation = Array(this.state.page_total).fill(0).map((ele,index)=>{
            return (<li key={1000+index*10} className="page-item">
                <button className="page-link" onClick={()=>this.fetch_items(index+1)}>{index+1}</button>
            </li>);
        });
        if(this.state.category=="blog"){
            table_title = <h2 className="my-3">Manage My Posts</h2>
            if(this.state.items==null){rows=<tr><td>You currently don't have a blog</td>
            <td>null</td><td>null</td><td>null</td></tr>;}
            else{
            rows = this.state.items.map((x,index)=>{
                var tt,ct,ac
                if(x.title.length>50){
                    tt = x.title.substr(0,27)+'...';
                }else{tt = x.title;}
                ct = datetime(x.created_at)
                ac = (<div>
                    <a type='button' className="btn btn-success btn-sm mx-1" href={"/manage/blogs/update/"+x.id}>Edit</a>
                    <a type='button' className="btn btn-success btn-sm mx-1" href="javascript:void(0);" 
                    onClick={()=>this.delete_items('blog',x.id)}>Del</a>
                </div>
                );
                return (<tr key={x.id}>
                    <td>{index-0+1}</td>
                    <td><a href={"/blogs/"+x.id} data-toggle="tooltip" data-placement="bottom" title={x.digest}>{tt}</a></td>
                    <td>{x.category}</td>
                    <td>{ct}</td>
                    <td>{ac}</td>
                </tr>)
            });}
            head = (
                <thead>
                    <tr>
                        <th>#</th>
                        <th>title</th>
                        <th>category</th>
                        <th>date</th>
                        <th>actions</th>
                    </tr>
                </thead>
            )
        }else if(this.state.category=='comment'){
            table_title = <h2 className="my-3">Manage My Comments</h2>;
            if(this.state.items==null){rows=<tr><td>You currently don't have a blog</td>
            <td>null</td><td>null</td><td>null</td><td>null</td></tr>;}
            else{
                rows = this.state.items.map((x,index)=>{
                    var tt,bt,ac;
                    if(x.content.length>50){
                        tt=x.content.substr(0,47)+'...'
                    }else{tt=x.content;}
                    if(x.title.length>30){
                        bt=x.title.substr(0,27)+'...';
                    }else{bt=x.title;}
                    ac = (
                        <div>
                            <a type='button' className="btn btn-success btn-sm mx-1" href="javascript:void(0);"
                            onClick={()=>this.delete_items('comment',x.id)}>Del</a>
                        </div>
                    )
                    return (
                        <tr key={x.id}>
                            <td>{index-0+1}</td>
                            <td><a href={"/blogs/"+x.blog_id} data-toggle="tooltip" data-placement="bottom" title={x.content}>{tt}</a></td>
                            <td><a href={"/blogs/"+x.blog_id} data-toggle="tooltip" data-placement="bottom" title={x.title}>{bt}</a></td>
                            <td>{datetime(x.created_at)}</td>
                            <td>{ac}</td>
                        </tr>
                    )    
                });
            };
            head = (
                <thead>
                    <tr>
                        <th>#</th>
                        <th>content</th>
                        <th>blog</th>
                        <th>date</th>
                        <th>actions</th>
                    </tr>
                </thead>
            )
        }else{

        }
        var navs;
        if(pagenation.length!=0){
            navs = (
                <ul className="pagination justify-content-center">
                    <li className="page-item">
                        <button className="page-link" disabled={this.state.page==1} onClick={()=>{
                            if(this.state.page>1){
                                this.fetch_items(this.state.page-1);
                            }
                        }}> {"<<"} </button> 
                    </li>
                    {pagenation}
                    <li className="page-item">
                        <button className="page-link" disabled={this.state.page==this.state.page_total} onClick={()=>{
                            if(this.state.page<this.state.page_total){
                                this.fetch_items(this.state.page-0+1);
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
        
        return (
            <div>
                {table_title}
                <table className="table table-striped">
                    {head}
                    <tbody>
                        {rows}
                    </tbody>
                </table>
                {navs}
            </div>
        )
       
    }
}

var cat = document.getElementById('list').innerText;
ReactDOM.render(<ManageList category={cat}/>,document.getElementById('list'));