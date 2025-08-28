I like to golf.

Golf has a few issues.

It takes a lot of time - unfortunately, I can't fix this.

However, the second issue, the lack of unified booking searching - that, I can fix.

Check out utahgolfbooking.com.
It's an AI agent that helps you

Infra:
- FlaskAPI backend..might change this to Node
- UI
- Caching: I added cacheing to make search retrieval faster (basically if last cache is more than 45 minutes old, a cache gets replaced)
    - So, I could constantly be caching results in the background, but this could get expensive. 
    - The downside is that a user might get a slow response once in a while. 

Future enhancements:
- Add checkout options in my app instead of routing user to book.

