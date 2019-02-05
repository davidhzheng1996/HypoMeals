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
                this.currentGoal = {'id':this.goals[key].id,'goalname':this.goals[key].goalname,'user':this.goals[key].user}
                $("#editGoalModal").modal('show');
              }
            }
          }
       },
       deleteGoal: function(userid,goalid){
         this.loading = true;
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
       updateGoal: function(userid,goalid) {
         this.loading = true;
         this.$http.post('/api/update_goal/'+ userid + '/'+goalid, this.currentGoal)
           .then((response) => {
             $("#editGoalModal").modal('hide');
             this.loading = false;
             this.getGoals(userid);
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   },
      viewGoal:function(goalid){
        window.location.href = '/goal/'+goalid
      }
   }
   });