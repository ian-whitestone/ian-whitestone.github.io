---
layout: post
title: Run more A/A tests
author: ianwhitestone
summary: How you can learn a lot by testing nothing
comments: false
---

{% include head.html %}


An A/A test is the same as an A/B test, but your treatment group receives the same experience as the control group. Instead of telling you the impact of a change, A/A tests help you build trust in your experimentation platform, and can surface a whole host of issues. 

Broadly speaking, there are two types of A/A tests you can run: offline and online.

## Offline testing

The offline A/A test helps you ensure that Type 1 errors (false positives) are controlled as expected (i.e. 5%). One way that higher than expected false positives can arise is when your variance estimation is incorrect. This can occur is when the [randomization unit is different than the analysis unit]({% post_url 2021-03-12-randomization-unit-analysis-unit %}). Running an offline A/A test can help you quickly identify whether you'll be prone to these issues.

The offline A/A test is very cheap to run. In a nutshell, it works by:

1. Querying a representative sample of your data. 
    - For example, if you have a set of users you plan to run your A/B experiment with, then use a recent copy of their actual data that covers the same length of time you plan to run your experiment for.
2. Randomly assign your subjects (user, session, pageview, etc.) to test or control
3. Calculate your relevant metric (clicks per users, # of conversions, etc.)
4. Run the appropriate test (t-test, two proportion z-test, etc.)<sup>1</sup>
5. Repeat steps 2-5 up 1000 times<sup>2</sup>
6. Analyze the results
    - Ensure that the % of false positives are in line with expectations. For example, if your p-value cutoff is 0.05, a common industry practice, you'd expect a 5% false positive rate.
    - Plot the distribution of p-values and check that they are uniform<sup>3</sup>.


## Online testing

Contrary to the offline test, the online A/A test is run on real users. Engineers must implement the randomization logic to assign the subjects to the appropriate group, and log the assignments. Both groups receive the control experience, so the new treatment experience does not need to be built. 

While offline tests help you validate your metrics & statistical tests, online A/A tests will help you validate the rest of your experimentation infrastructure. Are you seeing sample ratio mismatch in any of your segments? Is any new functionality required for the experiment working as intended? Are your data pipelines working as expected? For example, you may be logging users or events from a different place than your original system of record. You can use the online A/A test data to validate that your numbers line up, and you aren't leaking data anywhere.

## A/A tests in the wild

From just a handful of A/A tests I've run in my career, I've seen big benefits:

- An offline A/A test helped uncover a bug in one of our statistical tests which was leading to higher than expected false positive rates. The code made the common mistake of not adjusting the p-value cutoff when performing multiple comparisons, which doubled the rate of false positives for two group (i.e. A/B) tests.
- I used an offline A/A test simulation to validate that I could use a randomization unit (user) different than my analysis unit (session) without seeing a higher rate of false positives (see [this post]({% post_url 2021-03-12-randomization-unit-analysis-unit %}) for more context). This allowed me to run the A/B test using an existing session grain model & set of metrics, and avoid building anything new at the user grain. 
- Through an online A/A test I ran, we learned about some discrepancies between the new logging we added and our existing system of record. This caused us to change the data sources we used for our eventual A/B experiment metrics.
- For another experiment we ran in a new app we built, we were unable to properly randomize by user since the app did not have access to the necessary cookies when being loaded. As a hack around this limitation, we decided to rely on the browser cache to prevent a different version of the app being loaded for a user on each page view. We ran an online A/A test to understand this approach, and learned that using the browser cache would give us a good enough approximation of randomizing by user, since users rarely cleared their browser cache.
- Prior to running an A/B test that involved a [server side redirect](https://en.wikipedia.org/wiki/HTTP_302), we ran an online A/A' test<sup>4</sup>, where users in one group were redirected to the same page. This allowed us to isolate the impact of redirects alone, so that in our subsequent A/B test with redirects to a different page, we could have a sense of how much of the change was coming from redirects versus seeing the different page. The test also revealed some sample ratio mismatch (SRM) issues that arose from doing redirects. 
    * The redirects caused duplicate requests for certain browsers, which led to SRM at the session grain as each request created a new session. 
    * Certain users, like bots, won't follow redirects, which can cause them to drop off and not appear in your system of record, leading to SRM at the user grain when using the system of record.
    * Discovering these issues before our A/B test allowed us to switch to user grain metrics leveraging a new data source, which eliminated the SRM issues.

A/A tests are incredibly useful. We should run more of them.

## Notes

<sup>1</sup> The [github repo](https://github.com/marnikitta/stattests) from [this post](https://medium.com/@vktech/practitioners-guide-to-statistical-tests-ed2d580ef04f#6f38) has vectorized implementations of many different statistical tests available for use.

<sup>2</sup> The more A/A simulations you run, the better, as you'll get closer to the expected false positive rate. However, depending on the test or size of your dataset, this may take a long time. [Microsoft has found](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/p-values-for-your-p-values-validating-metric-trustworthiness-by-simulated-a-a-tests/) that 100 simulations is generally sufficient. More simulations can help produce smoother p-value distributions, which helps reduce false positives when testing for uniformity. If you want to run more simulations, employing parallelization or refactoring the statistical test functions to use vectorized numpy operations can help speed things up.

<sup>3</sup> You can easily run a [Kolmogorov–Smirnov test](https://en.wikipedia.org/wiki/Kolmogorov–Smirnov_test) to test whether the distribution is uniform: `scipy.stats.kstest(p_values, scipy.stats.uniform(loc=0, scale=1).cdf)`

<sup>4</sup> This is technically not an A/A test, since one group receives a different experience (the dummy redirect), hence the name A/A'


**Additional Reading**

- [Offline A/A tests at Microsoft](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/p-values-for-your-p-values-validating-metric-trustworthiness-by-simulated-a-a-tests/)
- Chapter 19 of [Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59)
    - This is a fantastic read, and considered the bible of experimentation. Everyone should own a copy.