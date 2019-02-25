new Vue({
  el: '#starting',
  data: {
  },
  mounted: function () {
    
  },
  methods: {
  }
});

var stuff = new vis.DataSet([
    {id: 1, content: 'item 1', start: '2013-04-20',group:1},
    {id: 2, content: 'item 2', start: '2013-04-14',group:1},
    {id: 3, content: 'item 3', start: '2013-04-18',group:1},
    {id: 4, content: 'item 4', start: '2013-04-16', end: '2013-04-19',group:2},
    {id: 5, content: 'item 5', start: '2013-04-25',group:2},
    {id: 6, content: 'item 6', start: '2013-04-27',group:2}
  ]);

var groups = new vis.DataSet([
  {
    id: 1,
    content: 'Group 1'
  },
  {
    id:2,
    content:'Group 2'
  }
]);

function test(){
    groups.add({id:3,content:'Group 3'})
}

var options = {
    stack: true,
    editable: true,
    orientation: 'top',
    onDropObjectOnItem: function(objectData, item, callback) {
        if (!item) { return; }
        alert('dropped object with content: "' + objectData.content + '" to item: "' + item.content + '"');
    }
};

// create a Timeline
var container = document.getElementById('visualization');
timeline1 = new vis.Timeline(container, stuff, groups, options);

function handleDragStart(event) {
    var dragSrcEl = event.target;

    event.dataTransfer.effectAllowed = 'move';
    var itemType = event.target.innerHTML.split('-')[1].trim();
    var item = {
        id: new Date(),
        type: itemType,
        content: event.target.innerHTML.split('-')[0].trim()
    };
    // set event.target ID with item ID
    event.target.id = new Date(item.id).toISOString();

    var isFixedTimes = (event.target.innerHTML.split('-')[2] && event.target.innerHTML.split('-')[2].trim() == 'fixed times')
    if (isFixedTimes) {
        item.start = new Date();
        item.end = new Date(1000 * 60 * 10 + (new Date()).valueOf());
    }
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


