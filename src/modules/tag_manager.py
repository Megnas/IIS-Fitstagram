from .db import db, Tag

def get_similar_tags(patern: str) -> [Tag]:
    like_pattern = f"%{patern}%"

    results = Tag.query.filter(
        Tag.name.ilike(like_pattern)
    ).all()

    return results

def is_tag_banner(tag: str) -> bool:
    tag: Tag = db.session.query(Tag).filter(Tag.name == tag).first()
    if tag:
        return tag.blocked
    return False

def get_valid_tag_id(tag_name: str) -> int:
    tag: Tag = db.session.query(Tag).filter(Tag.name == tag_name).first()
    if(tag):
        if tag.blocked:
            return None
        else:
            return tag.id
    else:
        try:
            new_tag = Tag(name=tag_name, blocked=False)
            db.session.add(new_tag)
            db.session.commit()
            return new_tag.id
        except:
            return None
        
def get_valid_tag(tag_name: str) -> Tag:
    tag: Tag = db.session.query(Tag).filter(Tag.name == tag_name).first()
    if(tag):
        if tag.blocked:
            return None
        else:
            return tag
    else:
        try:
            new_tag = Tag(name=tag_name, blocked=False)
            db.session.add(new_tag)
            db.session.commit()
            return new_tag
        except:
            return None