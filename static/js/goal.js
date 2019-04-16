var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     goals: [],
     loading: false,
     currentGoal: {},
     message: null,
     page:1,
     perPage: 10,
     pages:[],
     has_paginated:false,
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     newGoal: { 'goalname': '', 'user':null, 'deadline':'', 'enable_goal': false, 'timestamp':'','title':'' },
     dateError:'',
     error:'',
   },
   mounted: function() {
    this.getGoals();
   },
   methods: {
       getGoals: function(){
           this.loading = true;
           this.$http.get('/api/goal/')
               .then((response) => {
                  // console.log(response.data)
                   this.goals = response.data;
                   this.loading = false;
                   if(!this.has_paginated){
                      this.setPages();
                      this.has_paginated=true; 
                    }
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       getGoal: function(goalid){
          for(key in this.goals){
            // console.log('here')
            if(this.goals.hasOwnProperty(key)){
            // console.log(this.goals[key].id)
              if(this.goals[key].id == goalid){
                this.currentGoal = {'id':this.goals[key].id,'goalname':this.goals[key].goalname,'user':this.goals[key].user, 
                'deadline':this.goals[key].deadline,'enable_goal':this.goals[key].enable_goal}
                $("#editGoalModal").modal('show');
              }
            }
          }
       },
        setPages: function () {
        let numberOfPages = Math.ceil(this.goals.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      addPage: function (){
          this.pages.push(Math.ceil(this.goals.length / this.perPage)+1);
      },
      deletePage: function (){
        this.pages=[];
          let numberOfPages = Math.ceil(this.goals.length / this.perPage);
        for (let index = 1; index < numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      paginate: function (goals) {
      let page = this.page;
      // console.log(page)
      let perPage = this.perPage;
      let from = (page * perPage) - perPage;
      let to = (page * perPage);
      return  goals.slice(from, to);
    },
       deleteGoal: function(userid,goalid){
         this.loading = true;
         // TODO: use delimiters
         this.$http.post('/api/delete_goal/'+ userid + '/'+goalid)
           .then((response) => {
             this.loading = false;
             if((this.goals.length%this.perPage)==1){
                      this.deletePage();
                    }
             this.getGoals(userid);
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
       addGoal: function(userid,username) {
         this.newGoal.user = parseInt(userid,10);
         this.newGoal.title = username;
         var time = new Date().toLocaleString();
         this.newGoal.timestamp = time;
         var now = new Date();
         var date = new Date(this.newGoal.deadline);
         if(date < now){
            this.dateError = "Deadline cannot be in the past!"
            return;
         }
         this.loading = true;
         this.$http.post('/api/goal/',this.newGoal)
           .then((response) => {
           $("#addGoalModal").modal('hide');
           this.loading = false;
           if((this.goals.length%this.perPage)==0){
            this.addPage();
         }
           this.getGoals(userid);
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
         },
        updateGoal: function(goalid) {
         this.loading = true;
         var now = new Date();
         var date = new Date(this.currentGoal.deadline);
         if(date < now){
            this.dateError = "Deadline cannot be in the past!"
            return;
         }
         var time = new Date().toLocaleString();
         this.currentGoal.timestamp = time;
         this.$http.post('/api/update_goal/'+goalid, this.currentGoal)
           .then((response) => {
             $("#editGoalModal").modal('hide');
             this.loading = false;
             this.getGoals();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   },
      viewGoal:function(goalid){
        window.location.href = '/goal/'+goalid
      },
      Calculate:function(goalid){
        window.location.href = '/calculate_goal/'+goalid
      },
   },
   computed: {
    displayedGoals () {
      return this.paginate(this.goals);
    }
  },
   });