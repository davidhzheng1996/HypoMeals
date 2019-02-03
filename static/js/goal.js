var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     goals: [],
     loading: false,
     currentGoal: {},
     message: null,
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     newGoal: { 'goalname': '', 'user':null },
   },
   mounted: function() {},
   methods: {
       getGoals: function(userid){
           this.loading = true;
           console.log(this.newGoal)
           this.$http.get('/api/goal/'+userid)
               .then((response) => {
                  console.log(response)
                  console.log(response.data)
                   this.goals = response.data;
                   this.loading = false;
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
                this.currentGoal = this.goals[key]
                $("#editGoalModal").modal('show');
              }
            }
          }
       },
       deleteGoal: function(userid,goalid){
         this.loading = true;
         console.log('dsfsdaj sdalk;fj sadlk;fj sladk sadk;fj sa')
         // TODO: use delimiters
         this.$http.post('/api/delete_goal/' + userid + '/'+goalid)
           .then((response) => {
             this.loading = false;
             this.getGoals(userid);
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
       addGoal: function(userid) {
         this.newGoal.user = parseInt(userid,10)
         this.loading = true;
         this.$http.post('/api/goal/'+userid,this.newGoal)
           .then((response) => {
           $("#addGoalModal").modal('hide');
           this.loading = false;
           this.getGoals(userid);
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       updateGoal: function() {
         this.loading = true;
         console.log(this.currentGoal)
         this.$http.put('/api/goal/'+ this.currentGoal.id + '/',     this.currentGoal)
           .then((response) => {
             $("#editGoalModal").modal('hide');
             this.loading = false;
             this.currentGoal = response.data;
             this.getGoals();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   }
   }
   });