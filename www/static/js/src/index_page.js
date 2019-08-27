class Blog extends React.Component{
    constructor(props){
        super(props)
        this.state = {
            id : props.info.id,
            title : props.info.title,
            created_at : props.info.created_at,
            user_name : props.info.user_name,
            digest : props.info.digest,
            category: props.info.category
        }
    }
    datetime(time){
        var now = Date.now()/1000;
        if(now-time<60){
            return "Published a minute ago";
        }
        else if(now-time<3600){
            return "Published in an hour";
        }
        else if(now-time<86400){
            return "Published in a day";
        }
        else{
            var epoch = new Date(time*1000);
            return 'Published on '+(epoch.getMonth()+1)+'/'+epoch.getDate()+'/'+epoch.getFullYear();
        }
    }
    render(){
        return (
            <article className="my-3 p-3 shadow rounded" key={this.state.id}>
                <h2><a href={'/blogs/'+this.state.id}>{ this.state.title}</a></h2>
                <p className="text-muted" style={{float:"left"}}>  {this.datetime(this.state.created_at)}</p>
                <p className="text-muted mx-3" style={{float:"left"}}>{'tag:'+this.state.category}</p>
                <span className="text-muted text-right" style={{float:"right"}}>{this.state.user_name }</span>
                <p style={{clear:'both'}}>{ this.state.digest }</p>
                <p><a href={'/blogs/'+this.state.id}>Continue to read</a></p>
            </article>
        )
    }
}

class BlogList extends React.Component{
    constructor(props){
        super(props)
        this.state = {
            page : 1,
            category : props.category,
            blogs : null,
            total : null,
        }
        this.get_blogs(1);
    }

    get_blogs(p){
        //console.log(window.location.host)
        if(this.state.category!='index'){
            var url = "/api/blogs?page=" + p + "&category=" + this.state.category;
        }else{
            var url = "/api/blogs?page=" + p;}
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = ()=>{
            if(xhr.readyState === 4 && xhr.status === 200){
                const text = JSON.parse(xhr.responseText);
                if('error' in text){
                    //error ocurred
                    window.alert(text.error+'\n'+text.data+'\n'+text.message)
                }else{
                    this.setState({
                        page : p,
                        blogs: text.blogs,
                        total: text.total,
                    })
                }
            }
        }
        xhr.open('GET',url);
        xhr.send();
    }
    componentDidMount(){
        if(this.state.category!="index"){
            $('#nav_'+this.state.category).addClass('active')
        }
    }

    render(){
        if(this.state.blogs&&this.state.blogs.length!=0)
        {
            const blogs_list = this.state.blogs.map((b)=>{
                return <Blog key={b.id} info={b}/>
            })

            const button_list = Array(this.state.total).fill(0).map((ele,index)=>{
                return (<li key={1000+index*10} className="page-item">
                    <button className="page-link" onClick={()=>this.get_blogs(index+1)}>{index+1}</button>
                </li>);
            });

            return (
                <div>
                    {blogs_list}
                    <ul className="pagination justify-content-center">
                        <li className="page-item">
                            <button className="page-link" disabled={this.state.page==1} onClick={()=>{
                                if(this.state.page>1){
                                    this.get_blogs(this.state.page-1);
                                }
                            }}> {"<<"} </button> 
                        </li>
                        {button_list}
                        <li className="page-item">
                            <button className="page-link" disabled={this.state.page==this.state.total} onClick={()=>{
                                if(this.state.page<this.state.total){
                                    this.get_blogs(this.state.page+1);
                                }
                            }}> {">>"}</button>
                        </li>
                    </ul>
                </div>
            )
        }else{
            return <p>We currently don't have a record here</p>
        }
    }

}

var kind = document.getElementById("blogs").innerText
ReactDOM.render(<BlogList category={kind}/>,document.getElementById('blogs'))