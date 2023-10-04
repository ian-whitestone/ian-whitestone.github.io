---
layout: post
title: Farewell, Shopify ❤️
comments: false
---


## 👋

After three and a half beautiful years, today’s my last day at Shopify. Most people silently exit a company. I was planning to do just that, until my director [Mike](https://www.linkedin.com/in/mike-develin-20616b59/) encouraged me to write a farewell note. He said we need to celebrate people moving on and not let it go unnoticed. After some brief thought, I agreed. It would be a shame to not reflect on what I’ve gained from this experience, and acknowledge that it’s exactly because of my time here that I’m ready for what’s next. It’s tough to cover everything I’ve learned here, so I’m going to focus on two buckets which have had the largest impact on me.

## **product craft**

As an incoming data scientist, learning about the art of product was something I did not anticipate. I joined a brand new product area with ~7 other people (1 PM, 4 devs and 2 UX), which eventually grew into an org of over 100 people responsible for [Shopify Markets](https://www.shopify.ca/markets) and a new tax platform. Of course, this wasn’t a linear journey. We had false starts and features we ended up killing. There were even periods early on where we as a team were close to getting dissolved. All of these bumps along the way came with great universal lessons. I learned to fall in love with problems, and not solutions. To dream big, but start small. I saw first hand how big opportunities will always be sitting right in front of you, you just have to reach and grab them. This was relevant 3 years ago at Shopify and remains true today. Work hard, eyes open.

Being tightly embedded in a multi-disciplinary group will give you the opportunity to learn from experts in other crafts, you just need to take some initiative. I got to witness [Heather](https://twitter.com/HeatherMcGaw) run world class user research sessions, because I simply asked to join. I learned how we manage complex product rollouts, handle production incidents, and develop in large scale codebases because I invested in relationships with our amazing devs and became a sponge.

Regardless of what team you work on, one of the best features of working at Shopify is you get the closest thing possible to root level access to Tobi’s brain. Every couple months, I’d do a slack search for `from:@Tobi Lütke` and learn how he was thinking about the way things were built. One day it was *“Don’t stack abstractions”* in response to a discussion around abstracting [ActiveRecord](https://guides.rubyonrails.org/active_record_basics.html#what-is-active-record-questionmark)<sup>1</sup>. Another time it was the importance of setting good defaults in our product so everything just works out of the box. When deciding whether or not something should be built, he’d talk about the importance of having strong opinions and building based on that, rather than waiting for customer demand. Getting front row access to Tobi’s principled thinking and relentless focus on simplicity was easily one of the best things about working here.

## **data craft**

As close as I was to the product, I still spent 90% of my time living and breathing data. Shopify’s data team came about in 2014, back when none of the [“Modern Data Stack”](https://mattturck.com/data2021/) existed. Like other big tech companies from that era, they were forced to build many of the frameworks and tools that exist today as standalone companies.

As a [full stack data scientist](https://ianwhitestone.work/slides-v2/data-science-at-shopify.html), you get exposure to the data stack end to end and the people who built it. From data extraction and all the pitfalls with change data capture or deletes. To event tracking with kafka and the joys of duplicates, missed events and late arriving data. Out of memory errors, disk spill and lost containers<sup>2</sup>. Slow SQL queries and figuring out when it makes sense to build a new data model. We exist to add value with data, and navigating this stack and learning the ins and outs of each system was one of the favourite parts of my job.

Of course, I wasn’t alone in these endeavours. Across all crafts at Shopify, you’ll be surrounded with senior members who’ve been at it for 5 times as long as you have<sup>3</sup>. Take advantage of these opportunities and learn from the best. Be vocal and share your feedback about the platform. I did this frequently, and as a result got to participate in helping shape some of the new tooling we built.

Working in an end to end nature also allows you to see the full data value chain. I got to work on analysis that unblocked key product decisions, ran experiments that resulted in shipping changes that positively impacted millions of merchant’s businesses, and built data-driven products that abstracted away some of the [gnarlier aspects of commerce](https://www.shopify.ca/blog/us-canada-sales-tax-insights). Getting exposure to all these things takes time and persistence. Be patient, and the opportunities will come.

## onwards!

So, what’s next? A piece of advice that’s stuck with me for a long time is something my Dad said to me; that *“the worst thing that can happen in life is if you look back and say what if?"* <sup>4</sup>. While I could happily spend my career here, I’ve always wanted to take a shot at entrepreneurship and start a company<sup>5</sup>. With kids and a mortgage a few years out, it’s quickly become clear that now is the best time. As scared as I am, I know that 80 year old Ian in a rocking chair would be full of regret if he didn’t try this.

Without question, I’d have nowhere close to the level of confidence required to take this leap if it weren’t for my time at Shopify. So thanks to Tobi for creating this incredible place, and thanks to everyone I got to work with along the way. I am forever grateful.

### notes

<sup>1</sup> After being asked to elaborate, Tobi expanded on his point: *"Abstractions are bad unless they make something new possible or something that you really need to do 10x easier. The abstractions in rails are the ones that sit at this sweetspot. Stay close to vanilla rails as you can while solving the problem you have. Only deviate if you know exactly what you are doing. Never listen to architecture astronauts. Existence of arguments in favour of an abstraction doesn't even nearly clear the bar for adopting it."*

<sup>2</sup> I’m intentionally highlighting many of the more challenging aspects of working in data. Of course it’s not always like this. Yet, when things break and you push their limits is when you’ll be forced to go deep and really understand the ins and outs of how something works.

<sup>3</sup> Special shout out to Karl Taylor, Michael Styles and Khaled Hammouda, who taught me pretty much everything I know about Spark.

<sup>4</sup> Jeff Bezos said [something similar](https://www.youtube.com/watch?v=jwG_qR6XmDQ) when deciding to leave D.E. Shaw to start Amazon.

<sup>5</sup> More on this later, but I plan to build a B2B SaaS company in the data space. I’m happiest when I’m on the steepest part of the learning curve, and there’s no doubt that entrepreneurship and wearing all the hats required to build a company will bring this.
