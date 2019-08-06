//echarts 对象
let myChart = echarts.init(document.getElementById('container'));

//关系图属性
let graphOption = {
    tooltip: {
        formatter: function (params) {
            if (params.dataType == "node") {
                let shcool = params.data.school == undefined? SCHOOL_NAME: params.data.school,
                    institution = params.data.institution == undefined? INSTITUTION_NAME: params.data.institution;

                //设置提示框的内容和格式 节点和边都显示name属性
                return `<strong>节点属性</strong><hr>姓名：${params.data.label}<br>所属学校：${shcool}<br>所属学院：${institution}`;
            }
            else{
                if(params.data.visited){
                    return  `<strong>关系属性</strong><hr>拜访次数：${params.data.visited}次<br>参与活动：${params.data.activity}`;
                }
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
                    show : true,

                    //回调函数，显示用户名
                    formatter: function(params){
                        return params.data.label;
                    }
                }
            },
            force: {
                repulsion : [20,100],//节点之间的斥力因子。支持数组表达斥力范围，值越大斥力越大。
                gravity : 0.05,//节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。
                edgeLength :[20,100],//边的两个节点之间的距离，这个距离也会受 repulsion。[10, 50] 。值越小则长度越长
                layoutAnimation : true
            },

            lineStyle: {
                show : true,
                color: 'target',//决定边的颜色是与起点相同还是与终点相同
                curveness: 0.1//边的曲度，支持从 0 到 1 的值，值越大曲度越大。
            }
        }
    ]
};

/**
 * 重新加载关系图数据，把数据赋值给graphOption中的data
 * @param data 关系图数据
 */
function reloadGraph(data){
    if(!"nodes" in data) return;
    // console.log(data)
    let links = data.links;
    // console.log(nodes.length, links.length, cates.length);
    graphOption.series[0].data = data.nodes;
    graphOption.series[0].links = links;

    //let categories = [{name: ''}, {name: `${data.core_node}团队`}];
    let categories = data.categories;
    //graphOption.series[0].categories = categories;
    graphOption.series[0].categories = data.categories;
    graphOption.legend = [{
        data: categories.map(function (a) {
            return a.name;
        })
    }];
    myChart.setOption(graphOption);
    myChart.hideLoading();
}

//添加点击跳转事件
myChart.on('click', function (params) {
    //仅限节点类型
    if (params.dataType == 'node' && params.data.name != "0"){
        //页面
        window.open('/scholar/detail/'+params.data.name);
    }
});
//页面加载完成
reloadGraph(DATA);
