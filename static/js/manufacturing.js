new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     goals: [],
     loading: false,
     currentGoal: {},
     message: null,
     newGoal: { 'goal_sku_name': '', 'desired_quanitity': 0, 'id': null, 'user_id': null, 'sku_id': null, },
   },
   mounted: function() {
       this.getGoals();
   },
   methods: {
       getGoals: function(){
           this.loading = true;
           this.$http.get('/api/manufacture_goal/')
               .then((response) => {
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
       deleteGoal: function(id){
         this.loading = true;
         // TODO: use delimiters
         this.$http.delete('/api/manufacture_goal/' + id + '/')
           .then((response) => {
             this.loading = false;
             this.getGoals();
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
       addGoal: function() {
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