var myChart = echarts.init(document.getElementById('container'));


graph_option = {
    tooltip: {
        formatter: function (params) {
            if (params.dataType == "node") {
                //设置提示框的内容和格式 节点和边都显示name属性
                return `<strong>节点属性</strong><hr>姓名：${params.data.label}</b><br>所属学校：${params.data.school}<br>所属学院：${params.data.insititution}`;
            }
            else{
                return `<strong>关系属性</strong><hr>
                论文合作：${params.data.paper}次<br>专利合作：${params.data.patent}次<br>项目合作：${params.data.project}次<br>`;
            }
        }
    },

    // 图例
    legend: [
    ],
    animation: true,
    series : [
        {
            type: 'graph',
            layout: 'force',
            data: [],
            links: [],
            categories: [],

            // // 边的长度范围
            // edgeLength: [10, 50],

            //是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
            roam: true,

            // 当鼠标移动到节点上，突出显示节点以及节点的边和邻接节点
            focusNodeAdjacency:true,
            // 是否启用图例 hover(悬停) 时的联动高亮。
            legendHoverLink : true,

            label: {
                normal: {
                    position: 'inside',
                    show : false,

                    //回调函数，显示用户名
                    formatter: function(params){
                        return params.data.label;
                    }
                }
            },
            force: {
                repulsion : [10,100],//节点之间的斥力因子。支持数组表达斥力范围，值越大斥力越大。
                gravity : 0.1,//节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。
                edgeLength :[10,80],//边的两个节点之间的距离，这个距离也会受 repulsion。[10, 50] 。值越小则长度越长
                layoutAnimation : true
            },

            lineStyle: {
                show : true,
                color: 'target',//决定边的颜色是与起点相同还是与终点相同
                curveness: 0.1//边的曲度，支持从 0 到 1 的值，值越大曲度越大。
            }
        }
    ]
}

function reload_graph(data){
    if(!"nodes" in data) return;
    let nodes = data.nodes, links = data.links, cates = data.community;
    console.log(nodes.length, links.length, cates.length);
    graph_option.series[0].data = nodes;
    graph_option.series[0].links = links;

    categories = [];
    for (var i = 0; i < cates.length; i++) {
        categories[i] = {
            name: '社区' + (i + 1)
        };
    }
    graph_option.series[0].categories = categories;
    graph_option.legend = [{
        data: categories.map(function (a) {
            return a.name;
        })
    }];
    myChart.setOption(graph_option);
}

myChart.setOption(graph_option);

//添加点击跳转事件
myChart.on('click', function (params) {
    //仅限节点类型
    if (params.dataType != 'node')
        return;
    //页面
    window.open('/scholar/'+params.data.teacherId);
});

function format_data(data)
{
    let back_data = {
        "nodes" : [],
        "links" : [],
        "community" : data['community_data']
    };

    let nodes = data['nodes'];
    for(let index in nodes)
    {
        let node = nodes[index];
        node['label'] = node['name'];
        node['name'] = node['id'];
        //node['symbolSize'] = parseInt(node['centrality'] * 20 + 5);
        node['category'] = node['class'] - 1;
        delete node["id"];
        delete node["class"];
        back_data["nodes"].push(node);
    }
    let links = data['edges'];
    for(let index in links)
    {
        let link = links[index];
        link["value"] = link["weight"];
        delete link["weight"];
        back_data['links'].push(link)
    }

    return back_data;
}

$.get('/static/relation_data/back.json').done(function (data) {
    let graph = format_data(data);
    console.log(graph);
    reload_graph(graph);
});
