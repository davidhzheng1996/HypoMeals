var starting = new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    manufacturing_lines: new Set(),
    goals:[],
    groups: new vis.DataSet(),
    items: new vis.DataSet()
  },
  methods: {
    addGoal: function() {
        data = {"Kingdom Hearts 3":
                            {   "Cases":
                                    {   "manufacturing_lines":["man 1","man 2"],
                                        "time_needed":19
                                    },
                                "Disks":
                                    {
                                        "manufacturing_lines":["man 2","man 3"],
                                        "time_needed":30
                                    }
                            }
               }
        this.goals.push(data)
        for(key in data){
            if(data.hasOwnProperty(key)){
                for(key2 in data[key]){
                    if(data[key].hasOwnProperty(key2)){
                        for(key3 in data[key][key2].manufacturing_lines){
                            this.manufacturing_lines.add(data[key][key2].manufacturing_lines[key3])
                        }
                    }
                }
            }
        }
        for(let value of this.manufacturing_lines){
            this.groups.add({"id":value,"content":value})
        }
    }
  }
});

// 
//  var items = new vis.DataSet([
//     {id: 1, content: 'item 1', start: '2013-04-20'},
//     {id: 2, content: 'item 2', start: '2013-04-14'},
//     {id: 3, content: 'item 3', start: '2013-04-18'},
//     {id: 4, content: 'item 4', start: '2013-04-16', end: '2013-04-19'},
//     {id: 5, content: 'item 5', start: '2013-04-25'},
//     {id: 6, content: 'item 6', start: '2013-04-27'}
//   ]);

var timenow = new Date()
var timeend = new Date(timenow.getTime()+3600000*24)
timenow = timenow.toISOString()
timeend = timeend.toISOString()

var options = {
    stack: true,
    editable: true,
    orientation: 'top',
    start:timenow,
    end:timeend,
    onDropObjectOnItem: function(objectData, item, callback) {
        if (!item) { return; }
        alert('dropped object with content: "' + objectData.content + '" to item: "' + item.content + '"');
    },
    onAdd:function(item,callback){
        console.log(item)
        activity ={id: item.id, content: 'Drag Added', start: item.start,  end:new Date(item.start.getTime()+3600000*50),group:item.group}
        if(item.content!="new item"){
            stuff.add(activity)
        }
    }
};

// create a Timeline
var container = document.getElementById('visualization');
timeline1 = new vis.Timeline(container, starting.items, starting.groups, options);

function handleDragStart(event) {
    var dragSrcEl = event.target;

    event.dataTransfer.effectAllowed = 'move';
    var itemType = event.target.innerHTML.split('-')[1].trim();
    var item = {
        id: new Date(),
        content: event.target.innerHTML.split('-')[0].trim()
    };
    // set event.target ID with item ID
    event.target.id = new Date(item.id).toISOString();
    event.dataTransfer.setData("text", JSON.stringify(item));

    // Trigger on from the new item dragged when this item drag is finish
    event.target.addEventListener('dragend', handleDragEnd.bind(this), false);
}

function handleDragEnd(event) {
    // Last item that just been dragged, its ID is the same of event.target
    var newItem_dropped = timeline1.itemsData.get(event.target.id);

    var html = "<b>id: </b>" + newItem_dropped.id + "<br>";
    html += "<b>content: </b>" + newItem_dropped.content + "<br>";
    html += "<b>start: </b>" + newItem_dropped.start + "<br>";
    html += "<b>end: </b>" + newItem_dropped.end + "<br>";
    document.getElementById('output').innerHTML = html;
}

var items = document.querySelectorAll('.items .item');


for (var i = items.length - 1; i >= 0; i--) {
    var item = items[i];
    item.addEventListener('dragstart', handleDragStart.bind(this), false);
}


