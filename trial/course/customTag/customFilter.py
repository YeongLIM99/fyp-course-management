from django import template

register = template.Library()


# apply some filter according to the conditions where course is looped to be used in template

# used in view_result
@register.filter
def course_match(record, course):
    return record.filter(course_code=course)


# used in failed_list
@register.filter
def in_course(record, course):
    return record.filter(course_code=course, failed_twice=True, is_sent_failed=False)


