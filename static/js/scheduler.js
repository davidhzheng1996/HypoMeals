 var container = document.getElementById('visualization');

  // Create a DataSet (allows two way data-binding)
  var items = new vis.DataSet([
    {id: 1, content: 'item 1', start: '2013-04-20',group:1},
    {id: 2, content: 'item 2', start: '2013-04-14',group:1},
    {id: 3, content: 'item 3', start: '2013-04-18',group:2},
    {id: 4, content: 'item 4', start: '2013-04-16', end: '2013-04-19',group:2},
    {id: 5, content: 'item 5', start: '2013-04-25',group:2},
    {id: 6, content: 'item 6', start: '2013-04-27',group:2}
  ]);

  var groups = [
  {
    id: 1,
    content: 'Group 1'
    // Optional: a field 'className', 'style', 'order', [properties]
  },
  {
    id:2,
    content:'Group 2'
  }
]

  // Configuration for the Timeline
  var options = {};

  // Create a Timeline
  var timeline = new vis.Timeline(container, items, options,groups);

  function test(){
    items.add({id: 7, content: 'item 7', start: '2013-04-28',group:1})
  }