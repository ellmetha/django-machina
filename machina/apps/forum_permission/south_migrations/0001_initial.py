# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ForumPermission'
        db.create_table(u'forum_permission_forumpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('is_global', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_local', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'forum_permission', ['ForumPermission'])

        # Adding model 'GroupForumPermission'
        db.create_table(u'forum_permission_groupforumpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum_permission.ForumPermission'])),
            ('has_perm', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('forum', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.Forum'], null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
        ))
        db.send_create_signal(u'forum_permission', ['GroupForumPermission'])

        # Adding unique constraint on 'GroupForumPermission', fields ['permission', 'forum', 'group']
        db.create_unique(u'forum_permission_groupforumpermission', ['permission_id', 'forum_id', 'group_id'])

        # Adding model 'UserForumPermission'
        db.create_table(u'forum_permission_userforumpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum_permission.ForumPermission'])),
            ('has_perm', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('forum', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.Forum'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('anonymous_user', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'forum_permission', ['UserForumPermission'])

        # Adding unique constraint on 'UserForumPermission', fields ['permission', 'forum', 'user', 'anonymous_user']
        db.create_unique(u'forum_permission_userforumpermission', ['permission_id', 'forum_id', 'user_id', 'anonymous_user'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserForumPermission', fields ['permission', 'forum', 'user', 'anonymous_user']
        db.delete_unique(u'forum_permission_userforumpermission', ['permission_id', 'forum_id', 'user_id', 'anonymous_user'])

        # Removing unique constraint on 'GroupForumPermission', fields ['permission', 'forum', 'group']
        db.delete_unique(u'forum_permission_groupforumpermission', ['permission_id', 'forum_id', 'group_id'])

        # Deleting model 'ForumPermission'
        db.delete_table(u'forum_permission_forumpermission')

        # Deleting model 'GroupForumPermission'
        db.delete_table(u'forum_permission_groupforumpermission')

        # Deleting model 'UserForumPermission'
        db.delete_table(u'forum_permission_userforumpermission')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'forum.forum': {
            'Meta': {'ordering': "[u'tree_id', u'lft']", 'object_name': 'Forum'},
            u'_description_rendered': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('machina.models.fields.MarkupTextField', [], {'blank': 'True', 'null': 'True', u'no_rendered_field': 'True'}),
            'display_sub_forum_list': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('machina.models.fields.ExtendedImageField', [], {'max_length': '100', u'width': '100', 'null': 'True', 'blank': 'True', u'height': '70'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'last_post_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'link_redirects': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'link_redirects_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['forum.Forum']"}),
            'posts_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'topics_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'forum_permission.forumpermission': {
            'Meta': {'object_name': 'ForumPermission'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_global': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_local': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'forum_permission.groupforumpermission': {
            'Meta': {'unique_together': "((u'permission', u'forum', u'group'),)", 'object_name': 'GroupForumPermission'},
            'forum': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum.Forum']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            'has_perm': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum_permission.ForumPermission']"})
        },
        u'forum_permission.userforumpermission': {
            'Meta': {'unique_together': "((u'permission', u'forum', u'user', u'anonymous_user'),)", 'object_name': 'UserForumPermission'},
            'anonymous_user': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'forum': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum.Forum']", 'null': 'True', 'blank': 'True'}),
            'has_perm': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum_permission.ForumPermission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['forum_permission']