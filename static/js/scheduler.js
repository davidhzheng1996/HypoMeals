var starting = new Vue({
    el: '#starting',
    delimiters: ['${', '}'],
    data: {
        // for visualizing the activity palette
        unscheduled_goals: [],
        // is this useful?
        scheduled_goals: [],        
        // manufacturing lines on Timeline
        groups: new vis.DataSet(),
        // all active/orphaned activities on Timeline
        items: new vis.DataSet(),
        // all activities used for communicating with backend
        // ideally, items and activities should be binded together 
        activities: [],
        search_term: '',
        message: '',
        search_error: '',
        automate_error: '',
        report: {'manufacture_line':'', 'start_date':'', 'end_date':'',user:''},
        automate: {'start_date':'', 'end_date':'', 'activities': []},
        automate_response: {},
        active_manufacturing_activities:[],
        checkboxes: {},
        selected: false
    },
    methods: {
        addGoal: function () {
            // create manufacture activites for this goal in database
            $.get('api/mg_to_skus/'+this.search_term,(data)=>{
                // refresh activity palette
                this.populate()
                // console.log(data)
                // this.unscheduled_goals.push(data)
                // // add all new manufacturing lines 
                // let manufacturing_lines = []
                // for (key in data) {
                //     if (data.hasOwnProperty(key)) {
                //         for (key2 in data[key]) {
                //             if (data[key].hasOwnProperty(key2)&&key2!='deadline') {
                //                 for (key3 in data[key][key2].manufacturing_lines) {
                //                     manufacturing_lines.add(data[key][key2].manufacturing_lines[key3])
                //                 }
                //             }
                //         }
                //     }
                // }
                // group_ids = this.groups.getIds()
                // for (let value of manufacturing_lines) {
                //     if(!group_ids.includes(value)){
                //         this.groups.add({ "id": value, "content": value })
                //     }
                // }
            }).fail(function(xhr, status, error) {
                // this.search_error = xhr.responseText;
                // console.log(this.search_error)
                alert(xhr.responseText);
            });
        },
        saveTimeline: function(userid){
             let timeline_info = []
             this.activities.forEach((item) => {
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
             this.$http.post('api/save_scheduler',timeline_info)
             .then((response) => {
                alert('Success')
            })
             .catch((err) => {
                alert('Faiulre')
            })
        },
        getAutomation: function(){
            // check if any activity is selected
            starting.automate['activities'] = []
            Object.keys(starting.checkboxes).forEach(function(goal) {
                Object.keys(starting.checkboxes[goal]).forEach(function(sku) {
                    if(starting.checkboxes[goal][sku]['active'] == true) {
                        starting.automate['activities'].push({
                            'goal': goal,
                            'sku': sku
                        })
                    }
                })
            })
            if (starting.automate['activities'].length == 0) {
                alert('no activity is selected')
                $("#createReportModal").modal('hide');
            }
            let api_url = '/api/automate_scheduler';
            this.$http.post(api_url,this.automate)
             .then((response) => {
                this.automate_response = response.data;
                console.log(this.automate_response)
                item = {
                    'id': activity['sku'],
                    'group': activity['manufacturing_line'],
                    'manufacturing_lines': allowed_manufacturing_lines,
                    'sku': sku_name,
                    'start': activity['start'],
                    'end': activity['end'],
                    'time_needed': activity['duration'],
                    'style': style,
                    'status': activity['status'],
                    'deadline': deadline,
                    'goal': activity['goal_name'],
                    'content': sku_name
                }
                automate_response['scheduled_activities'].forEach(activity => {
                    this.items.push({
                        'id': activity['sku-id'],
                        'start': activity['start'],
                        'end': activity['end'],
                        'style': "background-color: purple;",
                        'content': activity['sku-name'],
                        'goal': activity['goal-name'],
                        ''
                    })
                })
                this.loading = false;
            })
             .catch((err) => {
                console.log(err);
                this.automate_error = err.bodyText;
            })
        },
        scheduleData: function(){
            
        },
        // ml_checkbox_click: function(ev, ml) {
        //     ml['all_active'] = true;
        //  },
        removeGoal: function(goal_name) {
            // remove goal from manufacture activites
            this.$http.get('api/remove_mg/'+goal_name)
             .then((response) => {
                 starting.populate()
            })
             .catch((err) => {
                 alert(err)
                 console.log(err)
            })
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
            // iterate through all skus to find the one user dragged
            let dragged_item = null
            this.activities.forEach(activity => {
                if (activity.goal === goal && activity.sku === sku) {
                    dragged_item = activity;
                } 
            })
            delete dragged_item.start
            delete dragged_item.end
            // set event.target ID with item ID
            event.target.id = dragged_item.id
            event.dataTransfer.setData("text", JSON.stringify(dragged_item))
        },
        actualTimeNeeded: function (start_time, hours_needed) {
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
        },
        setup_timeline: function() {
            $.get('api/get_scheduler',(response)=>{
                var timenow = new Date()
                var timeend = new Date(timenow.getTime() + 3600000 * 24)
                timenow = timenow.toISOString()
                timeend = timeend.toISOString()

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
                        item.status = 'active'
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
                        let actual_time_needed = starting.actualTimeNeeded(item.start, item.time_needed);
                        item.end = new Date(item.start.getTime() + actual_time_needed)
                        // visualize exceeding deadline
                        let deadline = new Date(item.deadline)
                        if (deadline < item.end) {
                            starting.message = 'sku ' + item.sku + ', completion time exceeds deadline ' + deadline.toString()
                            item.style = "background-color: red;"
                        } else {
                            starting.message = 'start time: ' + item.start.toString() + ',\n duration: ' + (actual_time_needed/3600000) + ', hours\n ' 
                                                + ', deadline: ' + deadline.toString()
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
                        starting.activities = starting.activities.filter(value => {
                            return !(value.sku === item.sku && value.goal === item.goal)
                        })
                        starting.activities.push(item)
                    },
                    onMoving: function (item, callback) {
                        if (item.start.getHours() < 8 || item.start.getHours() > 18) {
                            callback(null)
                            return
                        }
                        if(!item.manufacturing_lines.includes(item.group)){
                            callback(null)
                            return
                        } 
                        // calculate actual hours needed with night time 
                        let actual_time_needed = starting.actualTimeNeeded(item.start, item.time_needed);
                        item.end = new Date(item.start.getTime() + actual_time_needed)
                        // visualize exceeding deadline
                        let deadline = new Date(item.deadline)
                        if (deadline < item.end) {
                            starting.message = 'sku ' + item.sku + ', completion time exceeds deadline ' + deadline.toString()
                            item.style = "background-color: red;"
                        } else {
                            starting.message = 'start time: ' + item.start.toString() + ', duration: ' + (actual_time_needed/3600000) + ', hours ' 
                                                + ', deadline: ' + deadline.toString()
                            item.style = "background-color: green;"
                        }
                        // update activities
                        starting.activities.forEach(activity => {
                            if(activity.goal === item.goal && activity.sku === item.sku) {
                                activity.start = item.start
                                activity.end = item.end
                                activity.duration = item.duration
                            }
                        })
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
                        starting.activities.forEach(activity => {
                            if(activity.sku === item.sku && activity.goal === item.goal) {
                                activity.status = 'inactive'
                            }
                        })
                    }
                };
                // create a Timeline
                var container = document.getElementById('visualization');
                timeline1 = new vis.Timeline(container, this.items, this.groups, options);
        })
        },
        select_all_activities: function() {
            // set all unscheduled activities to be checked
            // [{goal_name(enabled): [sku_name(non_active),]},]
            this.unscheduled_goals.forEach(goal => {
                // console.log(goal)
                Object.keys(goal).forEach(goalname => {
                    let skus = goal[goalname]
                    Object.keys(skus).forEach(sku => {
                        if(sku !== 'deadline') {
                            this.checkboxes[goalname][sku]['active'] = this.selected
                        }
                    })
                })
            })
        },
        populate: function() {
            // console.log('populating')
            $.get('api/get_scheduler',(response)=>{
                if(!response['init']){
                    // console.log(response)
                    this.unscheduled_goals = response['unscheduled_goals']
                    this.scheduled_goals = response['scheduled_goals']
                    // active, inactive and orphaned activities
                    this.activities = response['activities']
                    // populate items
                    this.items.clear()
                    this.checkboxes = {}
                    this.activities.forEach(activity => {
                        if (activity.status === 'active' || activity.status === 'orphaned') {
                            // TODO: should update end datetime in the backend 
                            activity.start = new Date(activity.start)
                            let actual_time_needed = starting.actualTimeNeeded(activity.start, activity.time_needed);
                            activity.end = new Date(activity.start.getTime() + actual_time_needed)
                            this.items.add(activity)
                        }
                        goal = activity.goal
                        sku = activity.sku
                        if (this.checkboxes[goal] == null) {
                            this.checkboxes[goal] = {}
                        } ''
                        this.checkboxes[goal][sku] = {
                        'active': false
                        }
                    })
                    // populate groups
                    this.groups.clear()
                    this.activities.forEach(activity => {
                        activity.manufacturing_lines.forEach(ml => {
                            if(this.groups.get(ml) == null) {
                                this.groups.add({
                                    'id': ml,
                                    'content': ml
                                })
                            }
                        })
                    })
                    // console.log('repopuluate groups:')
                    // console.log(this.groups)
                }
                // console.log(this.checkboxes)
                // console.log(this.unscheduled_goals)
                // this.select_all_activities()
            })
        },
    },
    mounted: function () {
        this.setup_timeline()
        this.populate()
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
