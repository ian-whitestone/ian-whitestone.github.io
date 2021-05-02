---
layout: post
title: Lessons learned from online experiments
author: ianwhitestone
summary: 10 hard earned lessons from running online experiments 
image: images/lessons-learned-online-experiments/peeking.png
comments: false
---

{% include head.html %}

I've just wrapped up my 10th online experiment this week, so here's 10 hard-earned lessons from the past year. 


# Randomization units

For one experiment, our team wanted to measure the impact of changing the experience of some online shopping websites for a particular segment of users. I rather quickly decided that we would randomly assign each **session** to test or control, and measure the impact on conversion (purchase) rates. We had a nicely modelled dataset at the session grain that was widely used for analyzing conversion rates, and consequently, the decision to randomize by session seemed obvious.

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/sessions_split.png %}">
</p>

When you map out this setup, it would look something like you see below. Each session comes from some user, and we randomly assign their session to an experience. Our sessions are evenly split 50/50.

<p align="center">
    <img width="90%" src="{{ site.baseurl }}{% link images/choosing-randomization-unit/session_level_split.png %}">
</p>

However, if you look a little closer, this setup could result in some users getting exposed to both experiences. It's not uncommon for a user to have multiple sessions on a single store before they make a purchase. 

If we look at our user Terry, it's not unrealistic to think that the "Version B" experience they had in Session 2 influenced their decision to eventually make a purchase in Session 3, which would get attributed to the "Version A" experience.

<p align="center">
    <img width="90%" src="{{ site.baseurl }}{% link images/choosing-randomization-unit/session_level_split_w_memory.png %}">
</p>

This led me to my first very valuable lesson, which is to **💡think carefully when choosing your randomization unit**. Randomization units should be independent, and if they are not, you may not be measuring the true effect of your change. Another factor in choosing your randomization unit can come from the desired user experience. You can imagine that it would be confusing for some users if something significant was visibly different each time they came to a website.<sup>1</sup>

# Simulations

With 👆in mind, we decided to switch to user level randomization for the experiment, while keeping the session conversion rate as our primary success metric since it was already modelled and there was a high degree of familarity with the metric internally. 

However, after doing some reading I discovered that having a randomization unit (user) that is different than your analysis unit (session) could lead to issues. In particular, there were some articles<sup>2</sup> claiming that this could result in a higher rate of false positives. [One of them](https://towardsdatascience.com/the-second-ghost-of-experimentation-the-fallacy-of-session-based-metrics-fb65006d30ff) showed this plot:

<p align="center">
    <img width="60%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/skewed_p_values.png %}">
</p>

The intuition behind this is that your results could be highly influenced by which users land in which group. If you have some users with a lot of sessions, and a really high or low session conversion rate, that could heavily influence the overall session conversion rate for that group.

Rather than throwing my hands up and changing the strategy, I decided to run a simulation to see if we would actually be impacted by this. The idea behind the simulation was to take our population and simulate many experiments where we randomized by user and compared session conversion rates like we were planning to do in our real experiment. I then checked if we actually saw a higher rate of false positives, and it turned out we did not, so we decided to stick with our existing plan.<sup>3</sup>

The key lesson here was that **💡simulations are your friend**. If you're ever unsure about some statistical effect, it's very quick (and fun) to run a simulation to see how you'd be affected, before jumping to any conclusions.

# Influencing small decisions

Data is commonly used to influence big decisions with an obvious need for quantitative evidence. Does this feature positively impact our users? Should we roll it out to everyone? But there is also a large realm of much smaller decisions that could be equally influenced by data.

Around the time we were planning one of our experiments, the system responsible for rendering the relevant website content was in the process of being upgraded. The legacy system ("Renderer 1") was still handling ~15% of the traffic, while the new system ("Renderer 2") was handling the other 85%.

This posed a question to us: do we need to implement our experiment in the two different codebases for each rendering system? Based on the sizeable 15% still going to "Renderer 1", our initial thinking was yes. However, we decided to dig a bit deeper.

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/renderer_1.png %}">
</p>

With our experiment design, we'd only be giving the users the treatment/control experience on the first request in a given session. With that in mind, the question we actually needed to answer changed. Instead of what of % all requests across all users are served by "Renderer 2", we needed to look what % of first requests in a session are served by "Renderer 2", for the users we planned to include in our experiment.

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/renderer_2.png %}">
</p>

By reframing the problem, we learned that almost all of the relevant requests were being served by the new system, so we were safe to only implement our experiment in one code base.

A key lesson learned from this was that **💡data can and should inform both big & small decisions**. Big decisions like "should we roll out this feature to all users", and small decisions like "should we spend a few days implementing our experiment logic in another codebase". In this case, two hours of scoping saved at least two days of engineering work, and we learned something useful in the process.

This lesson was not necessarily unique to this experiment, but it's worth reinforcing. You can only identify these opportunities when you are working very closely with your cross discipline counterparts (engineering in this case), attending their standups & hearing the decisions they are trying to make. They usually won't come to you with these questions as the idea may not even come to their mind that this is something data could easily or quickly solve.

# Understanding the system 

For an experiment that involved redirecting the treatment group to a different URL, we decided to first run an A/A' test to validate that redirects were working as expected and not having a significant impact on our metrics.<sup>4</sup>

The A/A' setup looked something like this:

* A request for a URL comes into the backend
* The user, identified using a cookie, is assigned to control / treatment
    * The user & their assigned group is asychronously logged to Kafka
* If the user is in the control group they receive the rendered content (html, etc.) they requested
* If the user is in the treatment group, the server instead responds with a [302 redirect](https://en.wikipedia.org/wiki/HTTP_302) to the **same URL**
* This causes the user in the treatment group to make another request for the same URL
    * This time the server responds with the rendered content originally requested (a cookie is set in the previous step to prevent the user from being redirected again)

This may look like a lot, but for users this is virtually invisible. You'd only know if you were redirected if you opened your browser developer tools.

<p align="center">
    <img width="100%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/a_a_1.png %}">
</p>

Shortly into the experiment, I encountered my first instance of sample ratio mismatch (SRM). SRM is when the number of subjects in each group does not match your expectations. 

After inner joining the assigned users to our sessions system of record, we were seeing a slightly lower fraction of users in the test group compared to the control group, instead of the desired 50/50 split.

We asked ourselves why this could be happening. And in order to answer that question, we needed to understand how our system worked. In particular, how do records appear in the sessions data model, and what could be causing less records from our test group to appear in there?

<p align="center">
    <img width="100%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/a_a_2.png %}">
</p>

After digging through the source code of the sessions data model, I learned that it is built by aggregating a series of pageview events. These pageview events are emitted client side, which means that the "user" needs to download the html & javascript content our servers return, and then they will emit the pageview events to Kafka.

With this understanding in place, I now knew that some users in our test group were likely dropping off after the redirect, and consequently not emitting the pageview events.

<p align="center">
    <img width="100%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/a_a_3.png %}">
</p>

To better understand why this happening, we added some new server side logging for each request to capture some key metadata. The main hypothesis we had was this this was being caused by bots, since they may not be coded to follow redirects. Using this new logging, I tried removing bots by filtering out different user agents, and removing requests coming from certain IP addresses. This helped reduce the degree of SRM, but did not entirely remove it. It is likely that I was not removing all bots (as they are notoriously hard to identify) or there were potentially some real users (humans) who were dropping off in the test group.

Based on these results, I ended up changing the data sources used to compute our success metric and segment our users.

Despite the major head scratching this caused, I walked away with some really important lessons. First, **💡develop a deep understanding of your system**. By truly understanding how redirects and our sessions data model worked, we we're able to understand why we were seeing SRM and come up with alternatives to get rid of it.

The second lesson was to **💡log generously**. Our data platform team had made it incredibly simple & low effort to add new Kafka instrumentation, so we took advantage. The new request logging we initially added for investigative purposes ended up being used in the final metrics.

The final lesson was to **💡run more A/A tests**. By running the A/A' test, I was able to identify the sample ratio mismatch issues and update our metrics and data sources prior to running the final experiment. We also learned the impact of redirection alone, which helped with the final results interpretation in the eventual A/B test where we had redirection to a different URL.<sup>5</sup>

# Peeking 👀

In one experiment, I was constantly peeking at the results each day as I was particularly interested in the outcome. The difference in the success metric between the treatment & control groups had been holding steady for well over a week, until it took a nose dive in the last few days of the experiment. 

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/peeking.png %}">
</p>

After digging into the data, I found that this change was entirely driven by a single store with abnormal activity, and very high volumes, causing it to heavily influence the overall result. 

This served as a pleasant reminder to **💡beware of user skew**. With any rate based metric, your results can easily be dominated by a set of high volumes users (or in this case, a single high volume store).

And despite the warnings you'll hear, **💡peeking is good**. Peeking at the results each day allowed me to spot the sudden change in our metrics, and subsequently identify & remove the offending outlier.<sup>6</sup>


# Rabbit holes

In another experiment involving redirects, I was once again experiencing SRM. There was a higher than expected number of sessions in one group. In past experiments, similar SRM issues had been found to be caused by bots not following redirects, or weird behaviour with certain browsers.  

I was ready to chalk up this SRM to the same causes and call it a day, but there was some evidence that hinted something else may be at play. As a result, I ended up going down a big rabbit hole. The rabbit hole eventually led me to review the application code and our experiment qualification logic, where I learned that users in one group had all their returning sessions disqualified from the experiment due to a cookie that was set in their first session. 

For an e-commerce experiment, this has significant implications since returning users (buyers) are much more likely to purchase. It's not a fair comparison if one group contains all sessions and the other only contains the buyer's first sessions. After switching the analysis unit from session to user so that all user's sessions were considered, the results of the experiment changed from negative to positive overall.

Another important lesson learned: **💡go down rabbit holes**. In this case, the additional investigation turned out to be incredibly valuable as the entire outcome of the experiment changed after discovering the key segment that was inadvertently excluded. The outcome of a rabbit hole investigation may not always be this rewarding, but at minimum you will learn something you can keep in your cognitive backpack.

# Segmentation

Often times it may be tempting to look at your overall experiment results across all segments and call it a day. Your experiment is positive overall and you want to move on and roll out to the feature. This is a dangerous practice, as you can miss some really important insights.

<p align="center">
    <img width="100%" src="{{ site.baseurl }}{% link images/lessons-learned-online-experiments/segmented_results.png %}">
</p>

As we report results across all segments, it's important to remember that **💡we are measuring averages**. Positive overall does not mean positive for everyone, and vice versa. Always slice your results across key segments and look at the results. This can identify key issues like a certain browser or device where your design doesn't work, or a buyer demographic that is highly sensitive to the changes. These insights are just important as the overall result, as they can drive product changes or decisions to mitigate these effects.

# Going forward...

So as you run more experiments, remember:

- 💡Think carefully when choosing your randomization unit
- 💡Simulations are your friend
- 💡Data can, and should inform both big & small decisions
- 💡Develop a deep understanding of your system
- 💡Log generously
- 💡Run more A/A tests
- 💡Peeking is good
- 💡Beware of user skew
- 💡Go down rabbit holes
- 💡We are measuring averages

I certainly will.

## Notes


<sup>1</sup> For a more involved discussion on choosing your randomization unit, check out [this post]({% post_url 2021-01-31-choosing-randomization-unit %}).

<sup>2</sup> This [medium article](https://towardsdatascience.com/the-second-ghost-of-experimentation-the-fallacy-of-session-based-metrics-fb65006d30ff) first made me aware of the issue. It is also discussed in Chapter 18 of [Trustworthy Online Controlled Experiments](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59).

<sup>3</sup> You can consult [this post]({% post_url 2021-03-12-randomization-unit-analysis-unit %}) to learn more about when you can expect a higher rate of false positives when your randomization unit is different than the analysis unit, and how to deal with it when you are affected.

<sup>4</sup> Kohavi & Longbotham discuss experiments involving redirects in [this paper](http://kdd.org/exploration_files/v12-02-8-UR-Kohavi.pdf), and how it is important to run an A/A test (or rather, A/A' test, where A' uses a redirect) prior to the A/B test.

<sup>5</sup> I've written a [separate post]({% post_url 2021-03-28-run-more-a-a-tests %}) on running A/A tests for those who are interested in learning more.

<sup>6</sup> By peeking is good I mean looking at your results throughout the course of the experiment. To avoid the [peeking problems](https://gopractice.io/blog/peeking-problem/) most people are aware of, this can only be done in conjunction with following a strict experiment plan to collect a pre-determined sample size (i.e. don't get excited by the results and end the experiment early).