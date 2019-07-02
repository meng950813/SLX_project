var myChart = echarts.init(document.getElementById('container'));

var categories = [];
for (var i = 0; i < 6; i++) {
    categories[i] = {
        name: '社区' + (i + 1)
    };
}
graph.nodes.forEach(function (node) {
    node.itemStyle = null;
    node.category = node.code;
    // Use random x, y
    node.x = node.y = null;
    node.draggable = true;
});

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
    legend: [{
        // selectedMode: 'single',
        data: categories.map(function (a) {
            return a.name;
        })
    }],
    animation: true,
    series : [
        {
            type: 'graph',
            layout: 'force',
            data: graph.nodes,
            links: graph.links,
            categories: categories,

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
    }],
    myChart.setOption(graph_option);
}

myChart.setOption(graph_option);

