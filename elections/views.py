from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from .models import Election, Candidate, Candidate_Position, Vote, spoiled_votes
from authentication.models import AuditLog

# Show all elections
def elections(request):
    elections = Election.objects.filter(is_available=True)
    elections_closed = Election.objects.filter(is_available=False)
    return render(request, 'elections/elections.html', {'elections': elections,'elections_done': elections_closed})
# Show all elections
def elections_done(request):
    elections_closed = Election.objects.filter(is_available=False)
    return render(request, 'elections/elections.html', {'elections_done': elections_closed})
# Show all elections
def elections_done1(request):
    elections_closed = Election.objects.filter(is_available=False)
    return render(request, 'elections/elections.html', {'elections_done': elections_closed})


# Election detail -> summary of positions + candidates
def election_summary(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    positions = Candidate_Position.objects.filter(election=election).prefetch_related('candidates')
    user_votes = Vote.objects.filter(voter=request.user, election=election).values_list('position_id', flat=True)

    return render(request, 'elections/vote_page.html', {
        'election': election,
        'positions': positions,
        'user_voted_positions': list(user_votes),  # ✅ pass to template
    })




def positions_list(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    positions = Candidate_Position.objects.filter(election=election)
    return render(request, 'elections/positions.html', {
        'election': election,
        'positions': positions,
    })


def candidate_list(request, position_id):
    position = get_object_or_404(Candidate_Position, id=position_id)
    election = position.election
    candidates = Candidate.objects.filter(position=position)

    return render(request, 'elections/candidates.html', {
        'position': position,
        'candidates': candidates,
        'election': election,
    })


# Voting
def vote_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    election = candidate.election
    position = candidate.position  # ✅ get the position directly
    positions = Candidate_Position.objects.filter(election=election)

    # Check if election is active
    if not election.is_active():
        return render(request, 'elections/vote_result.html', {
            'error': 'This election is not currently active.'
        })
        

    # Check if user has already voted for this position
    existing_vote = Vote.objects.filter(
        voter=request.user,
        election=election,
        position=position   # ✅ use new field
    ).first()
    
    if existing_vote:
        return render(request, 'elections/vote_result.html', {
            'error': f'You have already voted for {position.name} in this election.'
        })

    # Record the vote
    Vote.objects.create(
        voter=request.user,
        candidate=candidate,
        election=election,
        position=position   # ✅ explicitly save position
    )
    # log the voting action
    AuditLog.objects.create(user=request.user, action=f'Voted for {candidate.name} in {election.name} for position {position.name}')

    # Check if user has voted in all positions
    user_votes = Vote.objects.filter(voter=request.user, election=election)
    voted_positions = user_votes.values_list('position', flat=True).distinct()  # ✅ use position field

    if len(voted_positions) == positions.count():
        request.user.has_voted = True
        request.user.save()

    return render(request, 'elections/vote_result.html', {
        'success': f'Your vote for {candidate.name} has been recorded successfully!',
        'candidate': candidate,
        'positions': positions,
        'election': election,
    })

# Abstain
def abstain_vote(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    
    # Check if user has already abstained for this election
    existing_abstain = spoiled_votes.objects.filter(
        voter=request.user,
        election=election,
    ).first()
  
    if existing_abstain:
        return render(request, 'elections/vote_result.html', {
            'error': 'You have already Abstained.'
        })
    
    if request.method == "POST":
        reason = request.POST.get("reason", "")
        spoiled_votes.objects.create(
            election=election,# ✅ track abstention per election
            voter=request.user,
            reason=reason
        )
        request.user.has_voted=True
        request.user.save()
        
        
        return render(request, "elections/abstain_result.html", {
            "success": f"Your abstention for {election.name} has been recorded.",
            "election": election,
        })

    # log the abstention action
    AuditLog.objects.create(user=request.user, action=f'Abstained from voting in {election.name} ')
    return render(request, "elections/spoiled.html", {
        "election": election,
        'done':existing_abstain
    })



def vote_result(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(election=election)
    positions = Candidate_Position.objects.filter(election=election)

    results = {}
    for position in positions:
        position_candidates = candidates.filter(position=position)
        winner = None
        if position_candidates:
            winner = max(position_candidates, key=lambda c: c.total_votes)
        results[position] = {
            "candidates": position_candidates,
            "winner": winner,
        }

    context = {
        "election": election,
        "results": results,
        "total_votes": candidates.aggregate(total=models.Count("votes"))["total"] or 0,
    }
    return render(request, "elections/results.html", context)

def active_elections(request):
    pass