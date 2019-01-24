import Vue from "vue";
import vuelidate from "vuelidate";
import vuelidateErrorExtractor, { templates } from "vuelidate-error-extractor";

Vue.use(vuelidate);
Vue.use(vuelidateErrorExtractor, { 
  /**
   * Optionally provide the template in the configuration. 
   * or use Vue.component("FormField", templates.singleErrorExtractor.foundation6)
   */
  template: templates.singleErrorExtractor.foundation6,
  messages: { required: "The {attribute} field is required" },
  // attributes: {
  //   email: "Email",
  //   first_name: "First name",
  //   last_name: "Last name"
  // }
});