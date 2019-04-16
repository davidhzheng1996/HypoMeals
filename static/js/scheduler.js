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
        message: '',
        search_error: '',
        report: {'manufacture_line':'', 'start_date':'', 'end_date':'',user:''},
        automate: {'start_date':'', 'end_date':''},
    },
    methods: {
        addGoal: function () {
            $.get('api/mg_to_skus/'+this.search_term,(data)=>{
                // add all skus to unscheduled goals
                console.log(data)
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
            }).fail(function(xhr, status, error) {
                // this.search_error = xhr.responseText;
                // console.log(this.search_error)
                alert(xhr.responseText);
            });
        },
        // addGoal: function () {
        //     this.$http.get('api/mg_to_skus/'+this.search_term).then((response)=>{
        //         // add all skus to unscheduled goals
        //         console.log(response)
        //         this.unscheduled_goals.push(response)
        //         // add all new manufacturing lines 
        //         for (key in response) {
        //             if (response.hasOwnProperty(key)) {
        //                 for (key2 in response[key]) {
        //                     if (response[key].hasOwnProperty(key2)&&key2!='deadline') {
        //                         for (key3 in response[key][key2].manufacturing_lines) {
        //                             this.manufacturing_lines.add(response[key][key2].manufacturing_lines[key3])
        //                         }
        //                     }
        //                 }
        //             }
        //         }
        //         group_ids = this.groups.getIds()
        //         for (let value of this.manufacturing_lines) {
        //             if(!group_ids.includes(value)){
        //                 this.groups.add({ "id": value, "content": value })
        //             }
        //         }
        //     }).catch((err) => {
        //         console.log(err)
        //     }); 
        // },
        saveTimeline: function(userid){
             let timeline_info = []
             this.items.forEach((item) => {
                timeline_info.push({
                    'user': userid,
                    'manufacturing_line': item['group'],
                    'sku': item['sku'],
                    'goal_name': item['goal'],
                    'start': item['start'],
                    'end': item['end'],
                    'duration': item['time_needed'],
                    'status': item['status']
                })
             })
            console.log(this.items)
            console.log(this.groups)
            console.log(this.scheduled_goals)
            console.log(this.unscheduled_goals)
            console.log(this.manufacturing_lines)
             this.$http.post('api/save_scheduler',timeline_info)
             .then((response) => {
                alert('Success')
            })
             .catch((err) => {
                alert('Faiulre')
            })
        },
        getAutomation: function(){
            let api_url = '/api/automate_scheduler';
            this.$http.post(api_url,this.automate)
             .then((response) => {
                this.loading = false;
            })
             .catch((err) => {
                console.log(err);
            })
        },
        removeGoal: function(goal_name) {
            // remove scheduled skus on Timeline 
            scheduled_goal_items = []
            this.items.forEach((item) => {
                if(item.goal === goal_name) {
                    // item.style = "background-color: gray;"
                    scheduled_goal_items.push(item)
                }
            })
            this.items.remove(scheduled_goal_items)
            // remove goal from both scheduled and unscheduled goal list
            var length = this.unscheduled_goals.length-1
            while(length>=0){
                if(Object.keys(this.unscheduled_goals[length])[0]==goal_name){
                    this.unscheduled_goals.splice(length,1)
                }
                length = length-1
            }

            var length = this.scheduled_goals.length-1
            while(length>=0){
                if(Object.keys(this.scheduled_goals[length])[0]==goal_name){
                    this.scheduled_goals.splice(length,1)
                }
                length = length-1
            }
            // console.log(length)
            // this.unscheduled_goals = this.unscheduled_goals.filter((unscheduled_goal) => {
            //     return (!goal_name in unscheduled_goal)
            // })
            // console.log(this.unscheduled_goals)
            // this.scheduled_goals = this.scheduled_goals.filter((scheduled_goal) => {
            //     return (!goal_name in scheduled_goal)
            // })
        },
        createReport: function(userid) {
            this.report.user = parseInt(userid)
         this.$http.post('/api/manufacture_schedule_report/',this.report)
           .then((response) => {
         $("#createReportModal").modal('hide');
         this.loading = false;
         this.viewReport();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       viewReport: function(){
        window.location.href = '/scheduler_report/'
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
                time_needed: this.unscheduled_goals[list_index][goal][sku].hours_needed,
                deadline: this.unscheduled_goals[list_index][goal].deadline,
            };
            // set event.target ID with item ID
            event.target.id = new Date(item.id).toISOString();
            event.dataTransfer.setData("text", JSON.stringify(item));

            // Trigger on from the new item dragged when this item drag is finish
            // event.target.addEventListener('dragend', handleDragEnd.bind(this), false);
        }
    },
    mounted: function () {
        $.get('api/get_scheduler',(response)=>{
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
                if(!response['init']){
                    this.items = new vis.DataSet(response['items'])
                    this.groups = new vis.DataSet(response['groups'])
                    this.unscheduled_goals = response['unscheduled_goals']
                    this.scheduled_goals = response['scheduled_goals']
                    console.log('this.items')
                    console.log(this.items)
                    console.log('this.groups')
                    console.log(this.groups)
                    console.log('this.unscheduled_goals')
                    console.log(this.unscheduled_goals)
                    console.log('this.scheduled_goals')
                    console.log(this.scheduled_goals)
                }
                // create a Timeline
                var container = document.getElementById('visualization');
                timeline1 = new vis.Timeline(container, this.items, this.groups, options);
                timeline1.on('doubleClick', function (properties) {});
        })
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
