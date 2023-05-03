//Update the progress
const pod_url = "/cloud/dashboard/cluster/01"

function update_progress()
{
    var num_cluster_text = document.getElementById("cluster_num").innerHTML;
    var num_cluster_progress = document.getElementById("cluster_bar")

    var num_pod_text = parseInt(document.getElementById("pod_num").innerHTML);
    var num_pod_progress = document.getElementById("pod_bar")

    var num_node_text1 = parseInt(document.getElementById("node_num1").innerHTML);
    var num_node_text2 = parseInt(document.getElementById("node_num2").innerHTML);
    var num_node_progress = document.getElementById("node_bar")

    if (parseInt(num_cluster_text) == 0)
    {
        num_cluster_progress.style.width = "0"
    }
    else{
        num_cluster_progress.style.width = (parseInt(num_cluster_text) / 20 * 100) + "%"
    }

    if (num_pod_text == 0){
        num_pod_progress.style.width = "0"
    }
    else{
        num_pod_progress.style.width = (parseInt(num_pod_text) / 15 * 100) + "%"
    }

    if (num_node_text1 == 0 & num_node_text2 == 0){
        num_node_progress.style.width = "0"
    }
    else {
        perc = num_node_text1 / num_node_text2 * 100
        num_node_progress.style.width = perc + "%"
    }

}

function update_status(){
    try
    {
        var status_elm = document.getElementById("init");
        status_text = status_elm.innerHTML

        nav_link1 = document.getElementById("nav-link1");
        nav_link2 = document.getElementById("nav-link2");

        title_link1 = document.getElementById("title-1");
        title_link2 = document.getElementById("title-2");
        title_link3 = document.getElementById("title-3");

        if (status_text !== 'Connected'){
            nav_link1.href = "#";
            nav_link2.href = "#";
            title_link1.href = "#"
            title_link2.href = "#"
            title_link3.href = "#"
            status_elm.style.backgroundColor = 'red';   
            
        }
    }
    catch (error)
    {
        console.log(error)
    }
    
    
    try {
        run_elm = document.getElementById("running-L");
        run_txt = run_elm.innerHTML;

        if (run_txt == 'Paused'){
            run_elm.style.backgroundColor = 'orange';
        }
        else{ run_elm.style.backgroundColor = 'green';}

    } 
    catch (error) {
        console.log(error)
    }

    try {
        run_elm = document.getElementById("running-M");
        run_txt = run_elm.innerHTML;

        if (run_txt == 'Paused'){
            run_elm.style.backgroundColor = 'orange';
        }
        else{ run_elm.style.backgroundColor = 'green';}

    } 
    catch (error) {
        console.log(error)
    }

    try {
        run_elm = document.getElementById("running-H");
        run_txt = run_elm.innerHTML;

        if (run_txt == 'Paused'){
            run_elm.style.backgroundColor = 'orange';
        }
        else{ run_elm.style.backgroundColor = 'green';}

    } 
    catch (error) {
        console.log(error)
    }
    
    

    

}

update_status()
update_progress()