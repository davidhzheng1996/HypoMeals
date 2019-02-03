var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     goals: [],
     loading: false,
     currentGoal: {},
     message: null,
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     newGoal: { 'goal_sku_name': '', 'desired_quantity': 0, 'user': null, 'sku': null, },
   },
   mounted: function() {
       // this.getGoals();
   },
   methods: {
       getGoals: function(userid){
           this.loading = true;
           this.$http.get('/api/manufacture_goal/'+userid)
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
       getGoal: function(id){
           this.loading = true;
           this.$http.get('/api/manufacture_goal/'+id+'/')
               .then((response) => {
                   this.currentGoal = response.data;
                   $("#editGoalModal").modal('show');
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       // deleteGoal: function(id){
       //   this.loading = true;
       //   // TODO: use delimiters
       //   this.$http.delete('/api/manufacture_goal/' + id + '/')
       //     .then((response) => {
       //       this.loading = false;
       //       this.getGoals();
       //     })
       //     .catch((err) => {
       //       this.loading = false;
       //       console.log(err);
       //     })
       // },
       addGoal: function(userid) {
         this.newGoal.user = parseInt(userid
         console.log(this.newGoal)
         this.loading = true;
         this.$http.post('/api/manufacture_goal/',this.newGoal)
           .then((response) => {
         $("#addGoalModal").modal('hide');
         this.loading = false;
         this.getGoals();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       updateGoal: function() {
         this.loading = true;
         console.log(this.currentGoal)
         this.$http.put('/api/manufacture_goal/'+ this.currentGoal.id + '/',     this.currentGoal)
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