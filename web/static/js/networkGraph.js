/*
* 
*/

// 初始化三个变量 节点/关系/关系文字/对象
var node_elements = null;
var link_elements = null;
var link_text_elements = null;

// 用来记录新建节点的 x y 坐标
var create_x = 0;
var create_y = 0;

var linkForce = d3.forceLink()
    .id(function (link) { return link.id })
    .strength(NETWORKCONFIG.link_strength);

var simulation = d3.forceSimulation()
    .force("link", linkForce);

// 更新数据
updateData(data_test);

function updateData(data) {
    setNetworkInfo(data);
    drawNetworkGraph(data);
    // 设置分析结果
    setResultInfo(data.results);
}


function setNetworkInfo(data) {
    var network_info = d3.select("#network-info");
    network_info.selectAll(".info").remove();
    network_info.append("p")
    .attr("class", "info")
    .text("节点数目：" + data.nodes.length);
    network_info.append("p")
    .attr("class", "info")
    .text("关系数目：" + data.links.length);
}



function drawNetworkGraph(data) {
    
    // 力导向图，默认
    if (NETWORKCONFIG.layout === 0) {
        linkForce.strength(NETWORKCONFIG.link_strength);
        simulation.alpha(1)
        .alphaDecay(0.002)
        .alphaMin(0.002)
            .force("r", null)
            .force("charge", d3.forceManyBody().strength(NETWORKCONFIG.node_charge).distanceMax(300))
            .force("center", d3.forceCenter((window.innerWidth - 250) / 2, (window.innerHeight - 60) / 2))
            .force("collision", d3.forceCollide(NETWORKCONFIG.node_size));
    }
    // 圆形布局
    else if (NETWORKCONFIG.layout === 1){
        data.nodes.forEach(function(node) {
            node.x = 0;
            node.y = 0;
        })
        linkForce.strength(0);
        simulation.force("charge", d3.forceCollide().radius(NETWORKCONFIG.node_size * 1.5))
        .force("r", d3.forceRadial(300, (window.innerWidth - 250) / 2, (window.innerHeight - 60) / 2))
        .alpha(5)
        .alphaDecay(0.1)
        .alphaMin(0.02);
    }
        
        
    // 连线对象
    link_elements = link_layout.selectAll("path")
    .data(data.links);
    link_elements.exit().remove();
    link_elements = link_elements.enter()
    .append("path")
    .attr("class", "link")
    .merge(link_elements)
    .attr("id", function(link, i){ return "link-" + i; })
    .on("mousedown.select-link", selectLink)
    .on("mouseover.hover-link", hoverLink);
    
    // 连线的文字
    link_text_elements = text_layout.selectAll("text")
    .data(data.links);
    link_text_elements.exit().remove();
    link_text_elements = link_text_elements.enter()
    .append("text")
    .attr("class", "link-text")
        .style("font-size", 10)
        .merge(link_text_elements)
        .style("display",  "block" );
        link_text_elements.selectAll("textPath").remove();
        link_text_elements.append("textPath")
        .attr("xlink:href", function (link, i) { return "#link-" + i; })
        .text(function(link) { return link.label; });
        
        // 节点对象
        node_elements = node_layout.selectAll(".node")
        .data(data.nodes);
        node_elements.exit().remove();
        node_elements = node_elements.enter()
        .append("g")
        .attr("class", "node")
        .merge(node_elements)
        .on("mouseover.hover-link", hoverNode)
        .call(d3.drag()
        .on("start", drag_start)
        .on("drag", draging)
        .on("end", drag_end));
        node_elements.selectAll("text").remove();
    node_elements.selectAll("circle").remove();
    node_elements.append("circle")
    .attr("r", NETWORKCONFIG.node_size);
    node_elements.append("text")
    .attr("class", "node-text")
    .attr("dy", ".35em")
        .attr("x", function (node) {
            return textBreaking(d3.select(this), node.name);
        })
        .style("display",  "block" );
        node_elements.filter(function(node) { return node.border === true; })
        .append("text")
        .attr("class", "tip")
        .attr("transform", "translate(15, -15)")
        .text("x");
        fill_circle();
        
    simulation.nodes(data.nodes)
    .on("tick", tick)
    .force("link")
    .links(data.links);
    simulation.restart();
    
}

function setResultInfo(results){
    if(results == undefined){
        return;
    }

    var result_info = d3.select("#result-info");
    result_info.selectAll(".info").remove();
    for (var i in results) {
        var item = results[i];
        if (item.title){
            result_info.append("strong")
            .attr("class", "info")
            .text(item.title + " : ");
        }
        result_info.append("p")
        .attr("class", "info")
        .text(item.msg);
    }
}



function tick() {
    node_elements.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    link_elements.attr("d", function(link) { return genLinkPath(link, NETWORKCONFIG.line_style); })
        .attr("marker-end", "url(#resolved)");
    link_text_elements.attr("dx", function(link) { return getLineTextDx(link); });
}

// 点击清空所有选中
container.on("click", function() {
    if (d3.event.ctrlKey === false) {
        d3.selectAll(".selected")
            .classed("selected", false);
        d3.selectAll(".finded")
            .classed("finded", false);
        d3.selectAll(".route")
            .classed("route", false);
        node_elements.each(function(d) {
            d.selected = false;
        });
    }
}).on("mousedown", function() {
    if (d3.event.which === 3) {
        create_x = d3.event.x;
        create_y = d3.event.y;
    }
});

// 清除所有临时绑定
function clearEvents() {
    container.on("mousemove.add-link", null);
    node_elements.selectAll("circle")
            .on("click.add-link", null)
            .classed("cursor-target", false);
    temp_layout.selectAll("line").remove();
}


// 颜色标记
d3.selectAll(".color-item")
    .on("click", function() {
        var click_item = d3.select(this);
        markColor(click_item.style("background-color"));
        d3.select("#color-marker")
            .style("left", this.offsetLeft + 2 + "px")
            .style("color", click_item.style("background-color"));
    });

d3.select("#node-color").on("change", function () {
    markColor(this.value);
});

function markColor(color_value) {
    var select_elements = d3.selectAll(".selected");
    var find_elements = d3.selectAll(".finded");
    select_elements.each(function(node) {
        node["color"] = color_value;
    });
    find_elements.each(function(node) {
        node["color"] = color_value;
    });
    fill_circle();
}


function fill_circle() {
    node_elements.select("circle")
        .style("fill", function(node,index) {
            if(node.class !== undefined)
                return color(node.class);
            return color(index % 10);
        })
        .style("stroke", function(node) {
            return "black";
        });
}

// 节点拖拽
function drag_start(node) {
    stopLayout();
    d3.event.sourceEvent.stopPropagation();
}

function draging(node) {
    node_elements.filter(function(d) { return d.selected; })
        .each(function (node) {
            node.x += d3.event.dx;
            node.y += d3.event.dy;
            d3.select(this).attr("transform", "translate(" + node.x + "," + node.y + ")");
        });
    link_elements.attr("d", function(link) { return genLinkPath(link, NETWORKCONFIG.line_style); });
    link_text_elements.attr("dx", function(link) { return getLineTextDx(link); });
}

function drag_end(node) {
    if (!d3.event.sourceEvent.ctrlKey) {
        node.selected = false;
        d3.select(this).classed("selected", false);
    }
}


// 掠过显示节点信息
function hoverNode(node) {
    var node_info = d3.select("#node-info");
    node_info.selectAll(".info").remove();
    var exclude_attr = ["x", "y", "vx", "vy", "selected", "previouslySelected", "color"];
    for (var key in node) {
        if (exclude_attr.indexOf(key.toString()) != -1) {
            continue;
        }
        node_info.append("p")
            .attr("class", "info")
            .text(key + ": " + node[key]);
    }
}

// 点击选中关系
function selectLink(link) {
    link.selected = true;
    d3.select(this).classed("selected", true);
}

// 掠过显示关系信息
function hoverLink(link) {
    var link_info = d3.select("#link-info");
    link_info.selectAll(".info").remove();
    var exclude_attr = ["x", "y", "vx", "vy", "index", "selected", "previouslySelected"];
    for(var key in link){
        // 可用来排除一些属性
        // if(exclude_attr.indexOf(item.toString()) != -1) {
        //     continue;
        // }
        var temp = link_info.append("p")
            .attr("class", "info");
        if (key != "source" && key != "target") {
            temp.text(key + ": " + link[key]);
        }
        else {
            temp.text(key + ": " + link[key]["name"]);
        }                    
    }
}