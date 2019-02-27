var starting = new Vue({
    el: '#starting',
    delimiters: ['${', '}'],
    data: {
        manufacturing_lines: new Set(),
        scheduled_goals: [], 
        manufacture_lines: [],
        skus: [],   
        // {sku_name, ingredient_name, goal_name, case_quantity, start_time, end_time, duration(hrs)}
        report_items: [],    
        // manufacturing lines
        // groups: new vis.DataSet(),
        // // skus
        // items: new vis.DataSet(),
        search_term: '',
        message: ''
    },
    methods: {
        addGoal: function (start, end, manufacture_line) {
            let report_skus = this.skus.filter((sku) => {
                return (sku.manufacturing_lines.includes(manufacture_line))
            })
            this.report_items = report_skus.map((sku) => {
                return {
                    'sku_name': sku.sku,
                    'goal_name': sku.goal,
                    'start_time': sku.start.toString(),
                    'end_time': sku.end.toString(),
                    'duration': (sku.end - sku.start),
                }
            })

            $.get('api/mg_to_skus/'+this.search_term,(data)=>{


                // add all skus to unscheduled goals
                this.unscheduled_goals.push(data)
                // add all new manufacturing lines 
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
                group_ids = this.groups.getIds()
                for (let value of this.manufacturing_lines) {
                    if(!group_ids.includes(value)){
                        this.groups.add({ "id": value, "content": value })
                    }
                }
            }); 
        },
    },
    mounted: function () {
        
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
        starting.message = ''
        // DO VALIDATIONS HERE
        // item is sku, group is manufacturing line
        // validate the time is within 8am to 6pm 
        if (item.start.getHours() < 7 || item.start.getHours() > 17) {
            starting.message = 'scheduled starting time outside of operation hours.'
            return 
        }
        // check if manufacturing line can make this sku
        if(!item.manufacturing_lines.includes(item.group)){
            starting.message = 'sku cannot be made on this manufacturing line.'
            return
        } 
        // calculate actual hours needed with night time 
        let actual_time_needed = actualTimeNeeded(item.start, item.time_needed);
        item.end = new Date(item.start.getTime() + actual_time_needed)
        // visualize exceeding deadline
        let deadline = new Date(item.deadline)
        if (deadline < item.end) {
            starting.message = 'sku ' + item.sku + ' completion time exceeds deadline ' + deadline.toString()
            item.style = "background-color: red;"
        } else {
            starting.message = 'start time: ' + item.start.toString() + '\n duration: ' + (actual_time_needed/3600000) + ' hours\n ' 
                                + 'deadline: ' + deadline.toString()
            item.style = "background-color: green;"
        }
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
        // visualize exceeding deadline
        let deadline = new Date(item.deadline)
        if (deadline < item.end) {
            starting.message = 'sku ' + item.sku + ' completion time exceeds deadline ' + deadline.toString()
            item.style = "background-color: red;"
        } else {
            starting.message = 'start time: ' + item.start.toString() + ' duration: ' + (actual_time_needed/3600000) + ' hours ' 
                                + 'deadline: ' + deadline.toString()
            item.style = "background-color: green;"
        }
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


