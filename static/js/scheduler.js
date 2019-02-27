var starting = new Vue({
    el: '#starting',
    delimiters: ['${', '}'],
    data: {
        manufacturing_lines: new Set(),
        unscheduled_goals: [],
        scheduled_goals: [],        
        // manufacturing lines
        groups: new vis.DataSet(),
        // skus
        items: new vis.DataSet(),
        search_term: '',
        error_message: ''
    },
    methods: {
        addGoal: function () {
            // data = {
            //     "Kingdom Hearts 3":
            //     {
            //         "Cases":
            //         {
            //             "manufacturing_lines": ["man 1", "man 2"],
            //             "time_needed": 7
            //         },
            //         "Disks":
            //         {
            //             "manufacturing_lines": ["man 2", "man 3"],
            //             "time_needed": 10
            //         }
            //     }
            // }
            // this.unscheduled_goals.push(data)
            // for (key in data) {
            //     if (data.hasOwnProperty(key)) {
            //         for (key2 in data[key]) {
            //             if (data[key].hasOwnProperty(key2)) {
            //                 for (key3 in data[key][key2].manufacturing_lines) {
            //                     this.manufacturing_lines.add(data[key][key2].manufacturing_lines[key3])}}}}}
                                
            //                     for (let value of this.manufacturing_lines) {
            //                         this.groups.add({ "id": value, "content": value })
            //                     }
            $.get('api/mg_to_skus/'+this.search_term,(data)=>{
                console.log(data)
                this.unscheduled_goals.push(data)
                console.log(this.unscheduled_goals)
                for (key in data) {
                    if (data.hasOwnProperty(key)) {
                        for (key2 in data[key]) {
                            if (data[key].hasOwnProperty(key2)&&key2!='deadline') {
                                for (key3 in data[key][key2].manufacturing_lines) {
                                    this.manufacturing_lines.add(data[key][key2].manufacturing_lines[key3])
                                }
                            }
                        }
                    }
                }
                console.log(this.manufacturing_lines)
                for (let value of this.manufacturing_lines) {
                    this.groups.add({ "id": value, "content": value })
                }
                console.log(this.groups)
            }); 
        },
        saveTimeline: function(){

        },

        onBlur: function (event) {
            if (event && this.search_term !== event.target.value)
                this.search_term = event.target.value
        },
        handleDragStart: function (list_index, goal, sku, event) {
            var dragSrcEl = event.target;
            event.dataTransfer.effectAllowed = 'move';
            // sku
            var item = {
                id: new Date(),
                content: event.target.innerHTML,
                goal: goal,
                sku: sku,
                manufacturing_lines: this.unscheduled_goals[list_index][goal][sku].manufacturing_lines,
                time_needed: this.unscheduled_goals[list_index][goal][sku].time_needed,
            };
            // set event.target ID with item ID
            event.target.id = new Date(item.id).toISOString();
            event.dataTransfer.setData("text", JSON.stringify(item));

            // Trigger on from the new item dragged when this item drag is finish
            // event.target.addEventListener('dragend', handleDragEnd.bind(this), false);
        }
    },
    mounted: function () {
        $("#search_input").autocomplete({
            minLength: 2,
            delay: 100,
            // https://stackoverflow.com/questions/9656523/jquery-autocomplete-with-callback-ajax-json
            source: function (request, response) {
                $.ajax({
                    url: "/api/search_goals/"+request.term,
                    type:'GET',
                    dataType: "json",
                    success: function (data) {
                        response(data)
                    }
                });
            },
            messages: {
                noResults: '',
                results: function () { }
            }
        });
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
var timeend = new Date(timenow.getTime() + 3600000 * 24)
timenow = timenow.toISOString()
timeend = timeend.toISOString()

actualTimeNeeded = function (start_time, hours_needed) {
    // in mili
    let time_needed = hours_needed * 3600000
    let actual_time = 0
    let start_day_end_time = new Date(start_time.getUTCFullYear(), 
                                      start_time.getUTCMonth(), 
                                      start_time.getUTCDate(),
                                      17, 
                                      0, 
                                      0, 
                                      0)
    actual_time += start_day_end_time - start_time
    time_needed -= start_day_end_time - start_time
    if (time_needed !== 0) {
        // night time of the day
        actual_time += 3600000 * 14
    }
    let full_days = Math.floor(time_needed / (3600000*10))
    actual_time += full_days * 3600000*24
    time_needed -= full_days * 3600000*10
    actual_time += time_needed
    // console.log(hours_needed)
    // console.log(start_time.toTimeString())
    // console.log((new Date(start_time.getTime() + actual_time)).toTimeString())
    return actual_time
}

var options = {
    stack: true,
    editable: true,
    orientation: 'top',
    start: timenow,
    end: timeend,
    onDropObjectOnItem: function (objectData, item, callback) {
        if (!item) { return; }
        alert('dropped object with content: "' + objectData.content + '" to item: "' + item.content + '"');
    },
    onAdd: function (item, callback) {
        error_message = ''
        // DO VALIDATIONS HERE
        // item is sku, group is manufacturing line
        // validate the time is within 8am to 6pm 
        if (item.start.getHours() < 7 || item.start.getHours() > 17) {
            error_message = 'scheduled starting time outside of operation hours.'
            return 
        }
        // check if manufacturing line can make this sku
        if(!item.manufacturing_lines.includes(item.group)){
            error_message = 'sku cannot be made on this manufacturing line.'
            return
        } 
        // calculate actual hours needed with night time 
        let actual_time_needed = actualTimeNeeded(item.start, item.time_needed);
        activity = { id: item.id, content: item.content, start: item.start, end: new Date(item.start.getTime() + actual_time_needed), group: item.group }
        // visualize exceeding deadline
        // let deadline = new Date(item.deadline)
        // if (deadline > activity.end) {
        //     error_message = 'sku ' + item.sku + ' completion time exceeds deadline ' + deadline.toTimeString()
        //     activity.style = "background-color: red;"
        // }
        item.end = new Date(item.start.getTime() + actual_time_needed)
        delete item.type
        starting.items.add(item)
        // store to backend 
        // move sku from unscheduled list to scheduled list
        starting.unscheduled_goals.forEach((unscheduled_goal) => {
            // check if item.goal is the key 
            if(item.goal in unscheduled_goal) {
                // goal[item.goal]: {sku-> {ml,time_needed}}
                // add sku to scheduled goals
                let goal_existing = false
                starting.scheduled_goals.forEach((goal) => {
                    if(item.goal in goal) {
                        goal_existing = true
                    }
                })
                // add new scheduled goal to scheduled goals 
                if(!goal_existing) {
                    let new_goal = {
                        [item.goal]: {}
                    }
                    starting.scheduled_goals.push(new_goal)
                }
                starting.scheduled_goals.forEach((scheduled_goal) => {
                    if(item.goal in scheduled_goal) {
                        Vue.set(scheduled_goal[item.goal], item.sku, unscheduled_goal[item.goal][item.sku])
                    }
                })
                // remove sku from unscheduled goals
                Vue.delete(unscheduled_goal[item.goal], item.sku)
            }
        })
    },

    onMoving: function (item, callback) {
        if (item.start.getHours() < 7 || item.start.getHours() > 17) {
            callback(null)
            return
        }
        // calculate actual hours needed with night time 
        let actual_time_needed = actualTimeNeeded(item.start, item.time_needed);
        item.end = new Date(item.start.getTime() + actual_time_needed)
        callback(item)
    },
    
    onRemove: function (item, callback) {
        // move item from scheduled to unscheduled 
        starting.scheduled_goals.forEach((scheduled_goal) => {
            if(item.goal in scheduled_goal){
                let scheduled_sku = scheduled_goal[item.goal][item.sku]
                starting.unscheduled_goals.forEach((unscheduled_goal) => {
                    if(item.goal in unscheduled_goal) {
                        Vue.set(unscheduled_goal[item.goal], item.sku, scheduled_sku)
                    }
                })
                Vue.delete(scheduled_goal[item.goal], item.sku)
            }
        })
        starting.items.remove(item)
    }
};

// create a Timeline
var container = document.getElementById('visualization');
timeline1 = new vis.Timeline(container, starting.items, starting.groups, options);
timeline1.on('doubleClick', function (properties) {});

// function handleDragEnd(event) {
//     // Last item that just been dragged, its ID is the same of event.target
//     var newItem_dropped = timeline1.itemsData.get(event.target.id);

//     var html = "<b>id: </b>" + newItem_dropped.id + "<br>";
//     html += "<b>content: </b>" + newItem_dropped.content + "<br>";
//     html += "<b>start: </b>" + newItem_dropped.start + "<br>";
//     html += "<b>end: </b>" + newItem_dropped.end + "<br>";
//     document.getElementById('output').innerHTML = html;
// }

// var items = document.querySelectorAll('.items .item');


// for (var i = items.length - 1; i >= 0; i--) {
//     var item = items[i];
//     item.addEventListener('dragstart', handleDragStart.bind(this), false);
// }


