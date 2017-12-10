########
Glossary
########

This is a comprehensive list of the terms used when discussing the functionalities of
django-machina.

.. glossary::
    :sorted:

    Attachment
        An attachment is a file associated with a forum message that other forum users may see in
        order to download it.

    Forum
       A forum is a container for messages. It is caracterized by a name and can be part of a tree
       of other forums. That way a forum may have a parent forum and multiples sub-forums. A forum
       is typed and can correspond to a **default forum**, a **category** or a **forum link**. A
       **default forum** contains mesages and can have sub-forums. A **category** can only contains
       default forums. A **forum link** redirects to a specified link and cannot have sub-forums.

    Forum permission
    	Forum permissions define what actions a user (anonymous or not) can do or not in a specific
        forum (eg. answer to forum topics).

    Post
       A post is a message embedded into a conversation that was submitted by a forum user. A post
       usually consists of a title and a text, but can also contain attachments.

    Topic
       A forum topic represents a conversation between forum users. It contains messages
       (or "posts") that were submitted by the forum users. A topic generally refers to the name of
       the conversation and the first message (or "post") embedded into it. A forum topic may
       contain additional contents like polls. A forum topics can be typed and can correspond to a
       **normal topic**, a **sticky topic** or an **announcement**. A **normal topic** is a regular
       conversation that will slide down the forum if no other posts are created into it and get
       bumped to the top of the forum otherwise. A **sticky topic** is a topic that is stuck at the
       top of the first page of a forum. An **announcement** is a topic that is stuck at the top of
       every page of a forum.
