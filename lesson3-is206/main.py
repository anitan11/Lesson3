import os
import webapp2
import jinja2

from google.appengine.ext import db

web_dir = os.path.join(os.path.dirname(__file__), 'web')
JINJA_ENVIRONMENT = jinja2.Environment(loader = jinja2.FileSystemLoader(web_dir), autoescape=True)

def render_str(template, **params):
    t = JINJA_ENVIRONMENT.get_template(template)
    return t.render(params)

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class PostDB(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	#key = str(key())

	def render(self):
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", p = self, key = str(self.key()))

class Blog(MainHandler):
    def get(self):
        posts = db.GqlQuery("select * from PostDB order by created desc limit 10")
        self.render('front.html', posts = posts)

class Post(MainHandler):
	def get(self):
		#key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		key = self.request.get('id')
		post = db.get(key)
		#key = int(key)
		#post = db.get(key)
		#post = db.get('select * from PostDB where key_db = key')

		if not post:
			self.error(404)
			return

		self.render("permalink.html", post = post)

class NewPost(MainHandler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')

		if subject and content:
			p = PostDB(parent = blog_key(), subject = subject, content = content)
			p.put()
			self.redirect('/blog')
		else:
			error = "subject and content, please!"
			self.render("newpost.html", subject=subject, content=content, error=error)

app = webapp2.WSGIApplication([('/blog', Blog),
                               ('/blogpost', Post),
                               ('/blog/newpost', NewPost),
                               ],
                              debug=True)
