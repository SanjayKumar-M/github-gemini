import os
import requests
import google.generativeai as genai
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'Evaluate a GitHub repository'

    def handle(self, *args, **kwargs):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

        github_url = input("Enter the GitHub URL: ")

        experience_level = input("Enter the experience level (Junior/Senior): ").lower()

        if experience_level not in ['junior', 'senior']:

            self.stdout.write(self.style.ERROR("Invalid experience level. Please enter 'Junior' or 'Senior'."))

            return  
        try:

            owner, repo = github_url.split('/')[-2:]

        except ValueError:

            self.stdout.write(self.style.ERROR("Invalid GitHub URL format."))
            
            return


        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

        headers = {'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'}

        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch the repository content."))
            return

        repo_content = response.json()
        if isinstance(repo_content, dict) and repo_content.get("message") == "Not Found":
            self.stdout.write(self.style.ERROR("The Repository is not found."))
            return


        files_content = []

        for file in repo_content:

            if file['type'] == 'file':

                file_response = requests.get(file['download_url'], headers=headers)

                if file_response.status_code == 200:

                    files_content.append(file_response.text)
        
        repo_code_content = "\n\n".join(files_content)

       
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",  #we can change this model if needed (pro or gemma or 1.0 pro)
            generation_config=generation_config,
        )

        chat_session = model.start_chat(
            history=[
               {
      "role": "user",
      "parts": [
        "This is the code, now I want you to consider yourself as a senior QA tester with 20 years of experience, and rate the bugs found by the candidates who wanna apply for the tester position. Make sure that this is internship so rate based on that.  Here some feedback on the above code, use this : 1)Line number 32,64,77,83 has element locator which is an absolute/static path instead of dynamic/ relative path. This is a wrong practice as the elements may change in future in UI and will create errors in our automation test executions.\nwe should always pick a relative path for finding the elements\n\n2)Line number 50,56,70,82 contains Thread.sleep(milliSeonds) which is a static wait and not a good practice to follow. Instead we can use dynamic waits (implicit,Explicit,Fluent..) based on the conditions for the waits.\n\n3)The code didn't followed Page Object Model.\n\n4)Did not imported necessary packages/classes in the code. example : ChromeDriver class, List.\n\n5)Line number 92 contains initialising of driver, but it is initialised only as a ChromeDriver. This way it is not possible to test cross browser testing while automation. Best way is to use WebDriver Interface while initialising Driver. Example : WebDriver driver;\nwe can initialise the driver with any browser class now and can perform cross browser testing\n\n6)Classes are declared as static members inside a non static class. This creates an error as static members can only be declared inside a static or the top level types.\n\n7)Line number 140 is throwing an IllegalStateException for validating the current page in broswer. IllegalStateException is generally for an errored driver, here the driver is still active and properly performing the actions. If the current url is not as expected we can simply write an \"Assert\" statement to validate the test case.",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, here is a breakdown of the bugs and feedback, along with a rating system suitable for evaluating intern candidates:\n\n**Bug Severity & Importance (For Interns)**\n\n* **Critical:**  Bugs that completely prevent functionality or indicate a fundamental misunderstanding of core concepts.\n* **Major:** Bugs that significantly impact functionality or demonstrate a lack of awareness of common best practices. \n* **Minor:** Bugs that have a small impact on functionality or represent opportunities for improvement in code style and maintainability.\n\n**Feedback on Candidate Code & Potential Interview Questions**\n\n1. **Locators (Lines 32, 64, 77, 83):**\n   * **Severity:** Major\n   * **Explanation:**  Over-reliance on absolute XPaths is a very common issue for beginners. It's crucial for testers to understand why relative locators or IDs are preferable for long-term maintainability.\n   * **Interview Questions:**\n     * \"Can you explain the different types of locators in Selenium?\"\n     * \"Why are absolute XPaths often discouraged? What are some alternatives?\" \n     * \"Let's say a developer changes the HTML structure slightly. How would that impact your tests, and what could you do to make them more resilient?\"\n\n2. **Static Waits (Lines 50, 56, 70, 82):**\n   * **Severity:** Major\n   * **Explanation:**  Relying on `Thread.sleep()` makes tests slow and unreliable. Understanding implicit and explicit waits is a key skill.\n   * **Interview Questions:**\n      * \"What are the disadvantages of using `Thread.sleep()` in automation?\"\n      * \"Describe the difference between implicit and explicit waits. When would you use each?\"\n      * \"How do waits impact the overall execution time and reliability of your test suite?\"\n\n3. **Lack of Page Object Model (POM):** \n   * **Severity:** Minor (Considering it's an internship, but emphasize importance)\n   * **Explanation:** The candidate attempts POM, but the implementation is not fully realized. This is a great opportunity to discuss the benefits of POM.\n   * **Interview Questions:**\n      * \"The code seems to have the beginnings of a Page Object Model. Can you describe what POM is and its advantages?\"\n      * \"How would you structure this test code differently if you were strictly following POM principles?\"\n\n4. **Missing Imports (ChromeDriver, List):**\n   * **Severity:** Minor (Easily fixed, but indicates attention to detail)\n   * **Explanation:**  Basic Java knowledge - IDEs usually help with imports, but the candidate should be able to recognize and fix these. \n   * **Interview Questions:**\n      *  During the coding portion, observe if the candidate can identify and resolve import issues.\n\n5. **Hardcoded ChromeDriver:** \n   * **Severity:** Minor \n   * **Explanation:** Using the `WebDriver` interface for browser flexibility is a good practice to introduce early in an intern's learning path.\n   * **Interview Questions:** \n      * \"If you wanted to run these tests on different browsers (like Firefox, Chrome, Edge), what changes would you need to make to the code?\" \n      * \"What's the benefit of using the `WebDriver` interface instead of a specific browser driver class?\"\n\n6. **Static Members Inside Non-Static Class:**\n   * **Severity:** Major (Fundamental Java concept)\n   * **Explanation:** Shows a lack of understanding of Java basics. This should be addressed, but could be forgiven in an early-stage intern.\n   * **Interview Questions:**\n      * \"Can you explain the difference between static and non-static members in Java?\"\n      * \"Why is it not possible to declare a static variable directly within a non-static class?\"\n\n7. **IllegalStateException for URL Validation:**\n   * **Severity:** Minor (Incorrect exception handling)\n   * **Explanation:** While not a major flaw, it highlights the candidate's approach to error handling and assertions.\n   * **Interview Questions:**\n      * \"What is the purpose of assertions in testing?  What happens when an assertion fails?\"\n      * \"Are there other types of exceptions that Selenium commonly throws? How would you handle them in your code?\"\n\n**Overall Intern Assessment**\n\n* **Technical Skills:** The candidate demonstrates some Selenium knowledge but needs guidance on best practices and Java fundamentals.\n* **Problem-Solving:** There's room for improvement in analyzing and addressing issues like locator fragility and static waits. \n* **Potential:**  With proper mentoring and training, the candidate shows potential for growth in test automation.\n\n**Recommendations**\n\n* **Focus on Fundamentals:** Ensure the intern has a solid grasp of Java basics (classes, objects, static members) and Selenium core concepts (locators, waits).\n* **Practical Experience:** Provide hands-on tasks and code reviews to reinforce best practices (POM, good locators, explicit waits).\n* **Encourage Exploration:** Challenge the intern to research and learn about different assertion libraries (like TestNG or JUnit) and cross-browser testing tools. \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Ok, now what is your job is the candidate will post their answers in their GitHub readme file, \"They are interns, and the bugs they found will not that much accurate\" and will not completely matching with the bugs (feedback) I gave you. SO your job is to analyse the solution given by the candidates and make decision on that like severity and rating, finally there should be a FINAL veridict or suggestion to the employer, that whether this is correct or not and a feedback on the candidate, and a final verdict saying whether they can continue with their application or not. Got it?",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. My role is to act as a Senior QA evaluating potential interns based on their attempted bug analysis, even though their GitHub README might not perfectly match the actual issues in the code. Here's how I'd approach this:\n\n**Evaluation Process**\n\n1. **Understanding:**  Carefully read the candidate's bug report in their README. Since they are interns, I'll focus on:\n   * **Effort:** Did they put in genuine effort to analyze the code? \n   * **Concepts:** Do they demonstrate a basic understanding of Selenium, even if their identification of specific issues is not 100% accurate?\n   * **Communication:**  Is their bug report clear, organized, and easy to understand?\n\n2. **Mapping:** I'll try my best to map their findings to the actual feedback points, even if there's not a one-to-one match. \n\n3. **Severity & Rating (Adjusted for Interns):**\n   * **High:** Candidate demonstrates a good grasp of core Selenium concepts and identifies issues closely related to the feedback points, even if the explanation isn't perfect.\n   * **Medium:** The candidate shows some understanding but makes notable errors in identifying or explaining the bugs. Potential is there, but needs more guidance.\n   * **Low:** The bug report is very basic, misses major issues, or demonstrates significant gaps in understanding.\n\n**Example Scenario (Let's assume this is what the candidate wrote):**\n\n**Candidate's GitHub README Bug Report**\n\n\"I reviewed the Java Selenium code and found these potential areas for improvement:\n\n* **Issue 1:** The code uses a lot of `Thread.sleep()` which slows down the tests. I think it's better to use something called 'explicit waits' instead, but I'm not sure how those work yet.\n* **Issue 2:**  The code seems very long and repetitive.  There might be a better way to organize it, but I'm still learning about good coding practices.\"\n\n**My Analysis as Senior QA**\n\n* **Mapping:**\n    * Issue 1 maps to the actual feedback point on Static Waits. \n    * Issue 2 is a general observation but could relate to the lack of proper POM (Page Object Model).\n\n* **Severity & Rating:** \n    * **Issue 1: Medium.** The candidate correctly identifies the use of `Thread.sleep()` as a problem and has heard of \"explicit waits.\" This shows they're on the right track, even if they don't have the full solution yet.\n    * **Issue 2: Low.** While true, the feedback is too vague. It doesn't show specific understanding of code organization principles.\n\n* **Feedback to Employer:**\n   \"The candidate's bug report demonstrates a basic understanding of Selenium. They were able to identify the issue with `Thread.sleep()` and suggested a possible improvement (explicit waits).  However, their understanding of code organization and design patterns seems limited at this stage. They would benefit significantly from guidance on best practices like Page Object Model and writing cleaner, more maintainable automation code.\"\n\n* **Final Verdict:** \n    * **Continue Application:** Yes.  Even though the bug report wasn't perfect, the candidate shows promise and a willingness to learn.\n    * **Next Steps:**\n        * During the interview, focus on the candidate's understanding of core Selenium concepts, especially waits.\n        * Provide resources (articles, tutorials) on Page Object Model and code organization. \n        * If possible, give them a small take-home coding challenge focused on implementing POM to assess their learning ability.\n\n**Important Note:** This is just one example. Adjust your evaluation based on the specific content of the candidate's GitHub README and your company's hiring standards for interns. \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Don't focus on the report, focus more on the bugs",
      ],
    },
    {
      "role": "model",
      "parts": [
        "You're right, focusing too much on the report format might distract from the core issue of technical skill assessment. Let me rephrase my approach to prioritize the candidate's bug-finding accuracy:\n\n**Evaluation Process (Bug-Centric)**\n\n1. **Identify Key Bugs:**  Refer back to my initial analysis of the code. The major issues likely include:\n   * **Overuse of Absolute XPaths:**  Impacts test maintainability.\n   * **Reliance on Static Waits:** Makes tests slow and unreliable.\n   * **Lack of Page Object Model:**  Leads to code duplication and makes maintenance harder.\n\n2. **Assess Candidate Findings:** Compare the candidate's reported bugs against the key issues. \n   * **Direct Hit:** The candidate clearly identifies and explains the core problem (e.g., \"Using `Thread.sleep()` is bad because...\").  **This demonstrates a good understanding.**\n   * **Partial Hit:** The candidate hints at the issue but doesn't fully grasp it or offers a vague solution. (e.g., \"The code uses a lot of pauses, which might not be good.\"). **This suggests potential but needs refinement.** \n   * **Miss:** The candidate completely misses a key issue. **This highlights a gap in knowledge.**\n\n3. **Severity Rating (Adjusted for Interns):**\n   * **High:**  The candidate identifies most key bugs (direct hits) and shows awareness of best practices, even if their solutions are not perfect.\n   * **Medium:** The candidate has a mix of direct and partial hits, indicating a developing understanding of Selenium fundamentals. \n   * **Low:**  Mostly misses or provides very vague descriptions of problems, suggesting a significant knowledge gap.\n\n**Example Scenarios & Feedback**\n\n**Scenario 1: Candidate Finds Some Key Bugs**\n\n* **Candidate README:** \"The code uses a lot of fixed XPaths, which could break easily. Also, waiting for a fixed time with `Thread.sleep()` isn't ideal.\"\n* **My Assessment:** \n    * **Severity:** Medium to High (depending on the level of explanation)\n    * **Feedback:** The candidate demonstrates awareness of locator fragility and static wait issues, which are positive signs. However, assess their understanding of alternatives (relative locators, explicit waits) during the interview.\n\n**Scenario 2:  Candidate Misses Major Issues**\n\n* **Candidate README:** \"The code looks okay, but it could use more comments. Maybe add some print statements for debugging?\"\n* **My Assessment:**\n    * **Severity:** Low\n    * **Feedback:** This indicates a lack of understanding of core Selenium concepts. The candidate's focus on superficial improvements suggests they need more fundamental training before being ready for test automation.\n\n**Final Verdict (Continue or Not?)**\n\n* **High/Medium Severity:** Generally suitable to proceed with the interview process. Use the interview to further evaluate their understanding and potential for growth.\n* **Low Severity:**  This is a judgment call. \n    * **Strong Potential in Other Areas?** If the candidate has other compelling skills (e.g., strong communication, eagerness to learn), you might give them a chance with the understanding that they need significant guidance.\n    * **Primarily a Technical Role?** If the internship heavily relies on Selenium automation, it's likely not a good fit at this stage. \n\n**Remember:** Interns are still learning! Focus on their potential and ability to grasp concepts, not just their current level of expertise. \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "So, what the thing is the company will send the file to the candidate either in java or python, now the candidate who applied for SDET junior role will analyse the code and will find the bugs and will write that in README.md file, now you need to analyse the readme file which was written by the candidate, also I provided some bug report as feedback to you right? Also use that, now you need to check how good the applicant found the bug and severity and as usual the final verdict of whether the employer can proceed with that applicant or not\n",
      ],
    }, 
    {
      "role": "model",
      "parts": [
        "Got it! I understand now. You want me to assess the candidate's bug-finding skills by comparing their GitHub README analysis to my professional evaluation of the provided code. My assessment will focus on how well the candidate identified the key issues and the severity of the missed bugs or misunderstandings. This will help determine if the candidate should move forward in the hiring process.\n\n**Here's the breakdown of my evaluation process:**\n\n1. **Review My Feedback:** I will carefully consider the bugs and feedback I provided, particularly focusing on the critical and major issues impacting the code's functionality, maintainability, and adherence to best practices.\n\n2. **Analyze Candidate's README:** I will read the candidate's README.md file, paying close attention to: \n    * **Bug Identification:** What bugs did they find? How accurately do these match the critical and major issues I identified?\n    * **Explanation & Understanding:** How well did they explain the problems? Do they demonstrate an understanding of why these are bugs and their potential impact?\n    * **Suggested Solutions:** Did they propose any solutions or improvements? Are these reasonable and in line with best practices?\n\n3. **Severity Assessment:** For each bug (or missed bug), I'll assign a severity level based on its potential impact and the candidate's demonstrated understanding.\n\n    * **High Severity (Critical):** Candidate accurately identified and explained a critical bug, demonstrating a good grasp of core concepts. Missing a critical bug will also fall under this category.\n    * **Medium Severity (Major):** Candidate identified a major bug, but the explanation might lack depth or the proposed solution isn't ideal. Missing a major bug will also fall under this category.\n    * **Low Severity (Minor):**  Candidate identified a minor bug or provided a superficial observation. Missing a minor bug is considered acceptable, especially for an entry-level position.\n\n4. **Overall Evaluation & Recommendation:** I'll provide a final verdict to the employer based on the overall severity of the findings and the candidate's demonstrated understanding of Selenium and testing principles. \n\n    * **Strong Candidate:** The candidate identified most or all critical and major bugs, showing a good understanding of core concepts. They may have also identified minor issues or offered insightful suggestions. I recommend proceeding with this candidate.\n    * **Potential but Needs Guidance:** The candidate caught some of the major issues but might have missed others or demonstrated a superficial understanding. Consider further evaluation during the interview process, focusing on the areas where they showed weaknesses. \n    * **Not a Good Fit:** The candidate missed most of the critical and major bugs, or their analysis demonstrated a significant lack of understanding. I recommend not moving forward with this candidate, as they might require extensive training and might not be ready for the role.\n\n**Example:**\n\nLet's say I provided feedback highlighting these key issues:\n\n* **Critical:** Hardcoded ChromeDriver, Static Members Inside Non-Static Class\n* **Major:**  Overuse of Absolute XPaths, Reliance on Static Waits \n* **Minor:**  Lack of comments, Could benefit from Page Object Model\n\nNow, let's consider a few candidate scenarios:\n\n**Candidate A:** \n\n* Identifies the hardcoded ChromeDriver issue and explains the importance of using the WebDriver interface for cross-browser testing.\n* Mentions the overuse of absolute XPaths and its potential impact on test maintainability.\n* Doesn't explicitly mention static waits but suggests exploring explicit waits for better synchronization.\n\n**Verdict:** Strong Candidate. They identified the critical bug and a major one, demonstrating a good understanding of core Selenium concepts.\n\n**Candidate B:**\n\n*  Focuses mostly on the lack of comments and suggests adding more print statements for debugging.\n*  Identifies the overuse of `Thread.sleep()` but doesn't offer a concrete alternative.\n\n**Verdict:**  Potential but Needs Guidance.  Missed the critical bug and showed a superficial understanding of the static wait issue. Further assessment during the interview is needed.\n\n**Candidate C:**\n\n* Doesn't identify any of the critical or major bugs. \n* Their analysis primarily focuses on code style and formatting, suggesting the use of a code formatter.\n\n**Verdict:**  Not a Good Fit. Candidate's analysis doesn't demonstrate a sufficient understanding of Selenium or automated testing principles. \n\n---\n\nBy following this process and providing specific examples from the candidate's README, I can help you evaluate their bug-finding skills and make informed hiring decisions. Please provide the candidate's README analysis, and I'll gladly review it to provide my assessment! \n",
      ],
    },
                {   
                    "role": "user",
                    "parts": [
                        f"GitHub URL: {github_url}\nExperience Level: {experience_level.capitalize()}\nRepository Content:\n{repo_code_content}",
                    ],
                },
              
            ]
        )

        response = chat_session.send_message("Generate the review now.")
        
        self.stdout.write(self.style.SUCCESS(response.text))


#some updated are required since there are lot to train because of the model upgrades