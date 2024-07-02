## Github Evaludator


1. The code didn't followed Page Object Model.

2. The WebDriver session opened by FirefoxDriver is not closed properly at the end of the test case. This could lead to resource leaks:
WebDriver driver = new FirefoxDriver();

3.  There is a nested class PagesforAutomationAssignment defined inside the Testcase101 class, which is not syntactically correct and will result in a compilation error:
      public class PagesforAutomationAssignment {
    public static void main(String[] args) {
        // Code
    }
}
This class should be defined outside the Testcase101 class.

4.  Thread.sleep(milliSeonds) on lines 50, 56, 70, and 82 is a static wait that should not be used. Alternatively, depending on the wait circumstances, we can employ dynamic waits (implicit, explicit, fluorescent, etc.).